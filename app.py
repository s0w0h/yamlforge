import subprocess
import requests
import yaml
import os
from flask import Flask, request, jsonify, send_file, render_template
import tempfile
from github import Github
import posixpath
import socket
import ipaddress
import shutil
import dns.resolver
import re

app = Flask(__name__, static_folder="assets", static_url_path="/assets")

env = os.environ.copy()
env["NODE_PATH"] = subprocess.check_output(["npm", "root", "-g"]).decode().strip()
API_KEYS = os.environ.get("API_KEY", "").split(",")


def extract_servers(source_url, field=None, max_depth=8):
    response = requests.get(source_url)
    response.raise_for_status()
    data = yaml.safe_load(response.text)

    servers = set()

    # 域名匹配正则表达式
    domain_pattern = re.compile(
        r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}"
    )
    # IPv4 地址匹配正则表达式
    ipv4_pattern = re.compile(
        r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    )
    # IPv6 地址匹配正则表达式
    ipv6_pattern = re.compile(
        r"(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"
    )

    def extract_from_dict(data, depth=0):
        if depth > max_depth:
            return
        for key, value in data.items():
            if isinstance(value, str):
                if ipv4_pattern.match(value) or ipv6_pattern.match(value):
                    servers.add(value)
                elif domain_pattern.match(value):
                    servers.add(value)
            elif isinstance(value, dict):
                extract_from_dict(value, depth + 1)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        extract_from_dict(item, depth + 1)
                    elif isinstance(item, str):
                        if ipv4_pattern.match(item) or ipv6_pattern.match(item):
                            servers.add(item)
                        elif domain_pattern.match(item):
                            servers.add(item)

    if field:
        field_data = extract_field(data, field, max_depth=max_depth)
        if isinstance(field_data, dict):
            extract_from_dict(field_data)
        elif isinstance(field_data, list):
            for item in field_data:
                if isinstance(item, dict):
                    extract_from_dict(item)
                elif isinstance(item, str):
                    if ipv4_pattern.match(item) or ipv6_pattern.match(item):
                        servers.add(item)
                    elif domain_pattern.match(item):
                        servers.add(item)
    else:
        extract_from_dict(data)
    return list(servers)


def extract_field(data, field, max_depth=8, current_depth=0):
    if current_depth > max_depth:
        return None

    keys = field.split(".")
    for key in keys:
        if isinstance(data, list):
            data = [
                extract_field(item, key, max_depth, current_depth + 1) for item in data
            ]
        elif isinstance(data, dict):
            data = data.get(key)
        else:
            return None
        if data is None:
            return None
    return data


def is_private_ip(ip_address):
    try:
        addr = ipaddress.ip_address(ip_address)
        return addr.is_private
    except ValueError:
        return False


def resolve_domain_recursive(domain, unique_servers, dns_servers, max_depth=8, depth=0):
    if depth >= max_depth:
        return

    resolver = dns.resolver.Resolver()
    resolver.nameservers = dns_servers
    # 设置更短的超时时间
    resolver.lifetime = 2.5  # 总解析超时时间
    resolver.timeout = 0.7  # 每个服务器的超时时间

    domain_lines = []
    ip_lines = []

    if domain not in unique_servers:
        unique_servers.add(domain)
        domain_lines.append(f"{domain}")

    try:
        # 尝试解析 A 记录 (IPv4)
        try:
            answers = resolver.resolve(domain, "A")
            for rdata in answers:
                ip_address = rdata.to_text()
                if ip_address not in unique_servers:
                    unique_servers.add(ip_address)
                    if not is_private_ip(ip_address):
                        ip_lines.append(f"{ip_address}")
        except (
            dns.resolver.NoAnswer,
            dns.resolver.NXDOMAIN,
            dns.resolver.NoNameservers,
            dns.exception.Timeout,
            dns.resolver.LifetimeTimeout,
        ) as e:
            # print(f"Error resolving {domain}: {e}")
            pass

        # 尝试解析 AAAA 记录 (IPv6)
        try:
            answers_v6 = resolver.resolve(domain, "AAAA")
            for rdata in answers_v6:
                ip_address = rdata.to_text()
                if ip_address not in unique_servers:
                    unique_servers.add(ip_address)
                    if not is_private_ip(ip_address):
                        ip_lines.append(f"{ip_address}")
        except (
            dns.resolver.NoAnswer,
            dns.resolver.NXDOMAIN,
            dns.resolver.NoNameservers,
            dns.exception.Timeout,
            dns.resolver.LifetimeTimeout,
        ) as e:
            # print(f"Error resolving {domain}: {e}")
            pass

        # 递归解析 CNAME 记录
        try:
            cname_answers = resolver.resolve(domain, "CNAME")
            for cname_rdata in cname_answers:
                cname = cname_rdata.to_text().strip(".")
                if cname not in unique_servers:
                    unique_servers.add(cname)
                    domain_lines.append(f"{cname}")
                    # 递归解析 CNAME 指向的域名
                    for line in resolve_domain_recursive(
                        cname, unique_servers, dns_servers, max_depth, depth + 1
                    ):
                        if "DOMAIN" in line:
                            domain_lines.append(line)
                        else:
                            ip_lines.append(line)
        except (
            dns.resolver.NoAnswer,
            dns.resolver.NXDOMAIN,
            dns.resolver.NoNameservers,
            dns.exception.Timeout,
            dns.resolver.LifetimeTimeout,
        ) as e:
            print(f"Error resolving {domain}: {e}")
            pass

    except Exception as e:
        pass

    # 返回所有收集到的结果
    for line in domain_lines:
        yield line
    for line in ip_lines:
        yield line


def generate_server_list(servers, dns_servers, max_depth=8):
    unique_servers = set()
    domain_lines = []
    ip_lines = []
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as f:
        filename = f.name
        for server in servers:
            if server not in unique_servers:
                unique_servers.add(server)
                if ":" in server:
                    if not is_private_ip(server):
                        ip_lines.append(f"{server}\n")
                elif "." in server and server.replace(".", "").isdigit():
                    if not is_private_ip(server):
                        ip_lines.append(f"{server}\n")
                else:
                    domain_lines.append(f"{server}\n")
                    for line in resolve_domain_recursive(
                        server, unique_servers, dns_servers, max_depth
                    ):
                        if "DOMAIN" in line:
                            domain_lines.append(f"{line}\n")
                        else:
                            ip_lines.append(f"{line}\n")

        f.writelines(domain_lines)
        f.writelines(ip_lines)

    return filename


def upload_to_github(
    filename, repo_name, token, branch="main", path="", rename="yaml.list"):

    g = Github(token)
    
    repo = g.get_repo(repo_name)
    file_path = posixpath.join(path, rename)

    try:
        contents = repo.get_contents(file_path, ref=branch)
        file_exists = True
    except Exception as e:
        if "Not Found" in str(e):
            file_exists = False
        else:
            raise e

    with open(filename, "r") as f:
        file_content = f.read()

    if file_exists:
        try:
            repo.update_file(
                contents.path,
                "Update proxies.server list",
                file_content,
                contents.sha,
                branch=branch,
            )
        except Exception as e:
            raise e
    else:
        try:
            repo.create_file(
                file_path,
                "Add proxies.server list",
                file_content,
                branch=branch,
            )
        except Exception as e:
            raise e


def process_yaml_with_js(yaml_file_path, js_file_path):
    with open(js_file_path, "r", encoding="utf-8") as js_file:
        js_code = js_file.read()

    with tempfile.NamedTemporaryFile(
        "w", delete=False, suffix=".yaml", encoding="utf-8"
    ) as temp_processed_yaml:
        temp_processed_yaml_path = temp_processed_yaml.name

    node_script = f"""
    const fs = require('fs');
    const yaml = require('js-yaml');
    const iconv = require('iconv-lite');

    {js_code}

    function processYaml() {{
        const yamlInput = fs.readFileSync('{yaml_file_path}');
        let yamlStr = iconv.decode(yamlInput, 'utf-8');
        
        // Handle BOM if present
        if (yamlStr.charCodeAt(0) === 0xFEFF) {{
            yamlStr = yamlStr.slice(1);
        }}

        const config = yaml.load(yamlStr);
        const modifiedConfig = main(config);
        const output = yaml.dump(modifiedConfig, {{ encoding: 'utf-8' }});
        fs.writeFileSync('{temp_processed_yaml_path}', output, 'utf-8');
    }}

    processYaml();
    """

    with tempfile.NamedTemporaryFile(
        "w", delete=False, suffix=".js", encoding="utf-8"
    ) as temp_node_file:
        temp_node_file.write(node_script)
        temp_node_file_path = temp_node_file.name

    try:
        subprocess.run(["node", temp_node_file_path], env=env, check=True)
        shutil.move(temp_processed_yaml_path, yaml_file_path)
    except subprocess.CalledProcessError as e:
        print(f"Error running node script: {e}")
        raise e
    finally:
        os.remove(temp_node_file_path)
        if os.path.exists(temp_processed_yaml_path):
            os.remove(temp_processed_yaml_path)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/listget", methods=["GET"])
def listget():
    provided_api_key = request.args.get("api_key", "")
    source = request.args.get("source")
    proxy = request.args.get("proxy", "")
    field = request.args.get("field", "proxies.server")
    repo = request.args.get("repo")
    token = request.args.get("token")
    branch = request.args.get("branch", "main")
    path = request.args.get("path", "")
    filename = request.args.get("filename", "yaml.list")
    dns_servers_str = request.args.get("dns_servers")
    max_depth_str = request.args.get("max_depth", 8)
    resolve_domains = request.args.get("resolve_domains", "false").lower() == "true"

    if API_KEYS:
        if provided_api_key not in API_KEYS:
            return jsonify({"error": "Invalid API key"}), 403

    try:
        max_depth = int(max_depth_str)
    except ValueError:
        max_depth = 8

    if not source:
        return jsonify({"error": "Missing source parameter"}), 400

    try:
        proxies = {}
        if proxy:
            if proxy.startswith("socks"):
                proxies = {"http": proxy, "https": proxy}
            elif proxy.startswith("http"):
                proxies = {"http": proxy, "https": proxy}
            else:
                return jsonify({"error": "Invalid proxy format"}), 400

        try:
            response = requests.get(source, proxies=proxies, timeout=60)
            response.raise_for_status()
            data = yaml.safe_load(response.text)
        except requests.exceptions.Timeout:
            return jsonify({"error": "Request timed out"}), 408
        except requests.exceptions.SSLError:
            return jsonify({"error": "SSL verification failed"}), 495
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Failed to fetch source: {str(e)}"}), 500
        except yaml.YAMLError as e:
            return jsonify({"error": f"Invalid YAML format: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

    if resolve_domains:
        servers = extract_servers(source, field, max_depth=max_depth)
    else:
        servers = extract_field(data, field, max_depth=max_depth)
        if not servers:
            return jsonify({"error": f"Field '{field}' not found in YAML"}), 400
        if isinstance(servers, list):
            servers = [s for s in servers if s]
        else:
            return jsonify({"error": "Invalid field structure"}), 400

    if resolve_domains:
        if dns_servers_str:
            dns_servers = dns_servers_str.split(",")
        else:
            dns_servers = ["223.5.5.5", "8.8.8.8"]

        for dns_server in dns_servers:
            socket.getaddrinfo(dns_server, None, socket.AF_UNSPEC, socket.SOCK_STREAM)

        temp_filename = generate_server_list(servers, dns_servers, max_depth=max_depth)
    else:
        temp_filename = tempfile.mktemp(suffix=".txt")
        with open(temp_filename, "w", encoding="utf-8") as f:
            for server in servers:
                f.write(f"{server}\n")

    try:
        if repo and token:
            try:
                upload_to_github(temp_filename, repo, token, branch, path, filename)
                return jsonify(
                    {
                        "message": f"File uploaded to GitHub successfully at {os.path.join(path, filename)}"
                    }
                )
            except Exception as e:
                return (
                    jsonify({"error": f"Failed to upload to GitHub: {str(e)}"}),
                    500,
                )
        else:
            return send_file(temp_filename, as_attachment=True, download_name=filename)
    finally:
        os.remove(temp_filename)


@app.route("/yamlprocess", methods=["GET"])
def yamlprocess():
    provided_api_key = request.args.get("api_key", "")
    source_url = request.args.get("source")
    proxy = request.args.get("proxy", "")
    merge_url = request.args.get("merge")
    filename = request.args.get("filename")

    if API_KEYS:
        if provided_api_key not in API_KEYS:
            return jsonify({"error": "Invalid API key"}), 403

    if not source_url or not merge_url:
        return jsonify({"error": "Missing source or merge URL"}), 400

    try:
        proxies = {}
        if proxy:
            if proxy.startswith("socks"):
                proxies = {"http": proxy, "https": proxy}
            elif proxy.startswith("http"):
                proxies = {"http": proxy, "https": proxy}
            else:
                return jsonify({"error": "Invalid proxy format"}), 400

        with tempfile.NamedTemporaryFile(
            "wb", delete=False, suffix=".yaml"
        ) as temp_yaml_file, tempfile.NamedTemporaryFile(
            "wb", delete=False, suffix=".js"
        ) as temp_js_file:

            with requests.get(
                source_url, stream=True, proxies=proxies
            ) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=8192):
                    temp_yaml_file.write(chunk)
            temp_yaml_file_path = temp_yaml_file.name

            with requests.get(
                merge_url, proxies=proxies
            ) as response:
                response.raise_for_status()
                temp_js_file.write(response.content)
            temp_js_file_path = temp_js_file.name

        try:
            process_yaml_with_js(temp_yaml_file_path, temp_js_file_path)

            download_filename = filename or os.path.basename(source_url)
            return send_file(
                temp_yaml_file_path, as_attachment=True, download_name=download_filename
            )
        finally:
            os.remove(temp_yaml_file_path)
            os.remove(temp_js_file_path)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error fetching files: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error processing files: {e}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=19527, timeout=300)
