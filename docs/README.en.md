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
- **GitHub Integration:** Can automatically upload generated `.list` files to a GitHub repository.
- **Simple Web Interface:** Provides a simple web interface for user configuration and operations.

## Usage Guide

### 1. Deployment

#### Docker (Recommended)

```bash
docker run -d --restart unless-stopped --name yamlforge -p 19527:19527 -e API_KEY=your_api_key s0w0h/yamlforge:latest
```

`-e API_KEY=your_api_key` is used to set the API key. Multiple API keys can be separated by commas, for example: `-e API_KEY=key1,key2,key3`.

#### Build Docker Image Manually

1. Clone the repository:
   ```bash
   git clone https://github.com/s0w0h/yamlforge.git
   ```
2. Modify the `Dockerfile`
   Set API_KEY
3. Build the image:
   ```bash
   cd yamlforge
   docker build -t yamlforge .
   ```
4. Run the container:
   ```bash
   docker run -d --restart unless-stopped --name yamlforge -p 19527:19527 -e API_KEY=your_api_key yamlforge
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
   npm install js-yaml iconv-lite
   ```
3. Set environment variables:
   ```bash
   export API_KEY=your_api_key
   ```
4. Run the application:
   ```bash
   python app.py
   ```

### 2. API Interface

After the application is running, you can use the following API interfaces for operations:

- **`/listget`:** Extracts YAML field lists and generates `.list` files.
- **`/yamlprocess`:** Processes YAML configurations using JavaScript scripts.

#### `/listget` Parameter Description

| Parameter         | Description                                                                                                                     | Required | Default Value       |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------- | -------- | ------------------- |
| `api_key`         | API Key                                                                                                                         | Yes      |                     |
| `source`          | URL of the YAML file                                                                                                            | Yes      |                     |
| `field`           | Field to extract (effective when `resolve_domains` is `false`)                                                                  | No       | `general.name`      |
| `repo`            | GitHub repository name (format: `username/repo`)                                                                                | No       |                     |
| `token`           | GitHub Personal Access Token                                                                                                    | No       |                     |
| `branch`          | GitHub branch name                                                                                                              | No       | `main`              |
| `path`            | File path in the GitHub repository                                                                                              | No       | Root directory      |
| `filename`        | Generated file name                                                                                                             | No       | `yaml.list`         |
| `dns_servers`     | Comma-separated list of DNS servers (effective when `resolve_domains` is `true`)                                                | No       | `223.5.5.5,8.8.8.8` |
| `max_depth`       | Maximum depth for field or domain resolution                                                                                    | No       | `8`                 |
| `resolve_domains` | Whether to resolve domains (if `true`, server addresses in the YAML configuration will be automatically extracted and resolved) | No       | `false`             |

**Example:**

```
http://IP:PORT/listget?api_key=your_api_key&source=YOUR_YAML_URL&field=YOUR_YAML_FIELD&repo=YOUR_REPO_NAME&token=YOUR_GITHUB_TOKEN&branch=YOUR_BRANCH_NAME&path=YOUR_PATH&filename=YOUR_FILE_NAME.list&dns_servers=223.5.5.5,119.29.29.29,1.1.1.1,8.8.8.8&max_depth=10&resolve_domains=true
```

#### `/yamlprocess` Parameter Description

| Parameter  | Description                                             | Required | Default Value    |
| ---------- | ------------------------------------------------------- | -------- | ---------------- |
| `api_key`  | API Key                                                 | Yes      |                  |
| `source`   | URL of the base YAML configuration file                 | Yes      |                  |
| `merge`    | URL of the JavaScript script for merging configurations | Yes      |                  |
| `filename` | Generated file name                                     | No       | Same as `source` |

**Example:**

 ```
http://IP:PORT/yamlprocess?api_key=your_api_key&source=YOUR_BASE_YAML_URL&merge=YOUR_MERGE_JS_URL&filename=YOUR_FILE_NAME
 ```

#### JavaScript Script Instructions

The JavaScript script needs to define a `main` function that takes a JSON object as a parameter and returns the processed JSON object.

### 3. Simple Web Interface

After the application is running, you can access a simple web interface at `http://IP:19527`, which implements most of the functionalities.

## Security Tips

- When deploying on a public network, it is strongly recommended to set an API key to prevent abuse of the API interface.
- Use HTTPS to secure API communication in production environments.
- Do not disclose your GitHub Personal Access Token.
- It is recommended to deploy YamlForge yourself and avoid using conversion websites from unknown sources to prevent configuration information leakage.

## Disclaimer

This project is for learning and research purposes only and should not be used for illegal purposes.

## License

[GPLv3](LICENSE)
