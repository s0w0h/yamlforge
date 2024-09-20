<p align="center">
<img src="../assets/yamlforge.png" alt="YamlForge" width="200">
</p>
<h1 align="center">
  YamlForge
</h1>

<p align="center">
 <a href="../README.md">简体中文</a> | <a href="README.en.md">English</a>
</p>

<p align="center">
  <a href="https://github.com/s0w0h/yamlforge/blob/main/LICENSE"><img src="../assets/GPL-3.0License.svg" alt="License"></a>
  <a href="https://github.com/s0w0h/yamlforge/pulls"><img src="../assets/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
</p>

**YamlForge** is a lightweight tool for extracting information from YAML configuration files and processing it using JavaScript scripts.

## Features

- **YAML Configuration Extraction:** Extracts specified fields from remote YAML files and generates `.list` files.
- **JavaScript Script Processing:** Supports modifying and merging YAML configurations using JavaScript scripts.
- **GitHub Integration:** Can automatically upload generated `.list` files to GitHub repositories.
- **Simple Web Interface:** Provides a simple web interface for user configuration and operation.

## Usage Guide

### 1. Deployment

#### Docker (Recommended)

```bash
docker run -d --restart always --name yamlforge -p 19527:19527 s0w0h/yamlforge:latest
```

#### Build Docker Image Manually

1. Clone the repository:
   ```bash
   git clone https://github.com/s0w0h/yamlforge.git
   ```
2. Build the image:
   ```bash
   cd yamlforge
   docker build -t yamlforge .
   ```
3. Run the container:
   ```bash
   docker run -d --restart always --name yamlforge -p 19527:19527 yamlforge
   ```

#### Run Directly (Python 3.9)

1. Clone the repository:
   ```bash
   git clone https://github.com/s0w0h/yamlforge.git
   ```
2. Install dependencies:
   ```bash
   cd yamlforge
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```

### 2. API Interface

After the application is running, you can operate it through the following API interfaces:

- **`/listget`:** Extracts YAML field lists and generates `.list` files.
- **`/yamlprocess`:** Processes YAML configurations using JavaScript scripts.

#### `/listget` Parameter Description

| Parameter | Description | Required | Default Value |
|---|---|---|---|
| `source` | URL of the YAML file | Yes |  |
| `field` | Field to extract | No | `general.name` |
| `repo` | GitHub repository name (format: `username/repo`) | No |  |
| `token` | GitHub personal access token | No |  |
| `branch` | GitHub branch name | No | `main` |
| `path` | File path in the GitHub repository | No | Root directory |
| `filename` | Generated file name | No | `server.list` |
| `dns_servers` | Comma-separated list of DNS servers (only supports UDP DNS) | No | `223.5.5.5,8.8.8.8` |
| `max_depth` | Maximum depth of field or domain name resolution parsing | No | `8` |
| `resolve_domains` | Whether to resolve the domain name (if `true`, the server address in the yaml configuration will be extracted and the domain name will be resolved automatically) | No | `false` |

For example:
 ```
http://IP:PORT/listget?source=YOUR_YAML_URL&field=YOUR_YAML_FIELD&repo=YOUR_REPO_NAME&token=YOUR_GITHUB_TOKEN&branch=YOUR_BRANCH_NAME&path=YOUR_PATH&filename=YOUR_FILE_NAME.list&dns_servers=223.5.5.5,119.29.29.29,1.1.1.1,8.8.8.8&max_depth=10&resolve_domains=true
 ```

#### `/yamlprocess` Parameter Description

| Parameter | Description | Required | Default Value |
|---|---|---|---|
| `source` | URL of the base YAML configuration file | Yes |  |
| `merge` | URL of the JavaScript script for merging configurations | Yes |  |
| `filename` | Generated file name | No | Same as `source` |

For example:
 ```
http://IP:PORT/yamlprocess?source=YOUR_BASE_YAML_URL&merge=YOUR_MERGE_JS_URL&filename=YOUR_FILE_NAME
 ```

#### JavaScript Script Description

The JavaScript script needs to define a `main` function that takes a JSON object as a parameter and returns the processed JSON object.

### 3. Simple Web Access

After the application is running, you can access a simple web interface through `http://IP:19527`, which implements most of the functions.

## Security Tips

- Use HTTPS to protect API communication in production environments.
- Do not disclose your GitHub personal access token.
- It is recommended to deploy YamlForge yourself and avoid using conversion websites from unknown sources to prevent configuration information leakage.

## Disclaimer

This project is for learning and research purposes only and should not be used for illegal purposes.

## License

[GPLv3](LICENSE)
