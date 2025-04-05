<p align="center">
<img src="../assets/yamlforge.png" alt="YamlForge" width="200">
</p>
<h1 align="center">
  YamlForge
</h1>

<p align="center">
 <a href="docs/README.en.md">English</a> | <a href="README.md">简体中文</a>
</p>

<p align="center">
  <a href="https://github.com/s0w0h/yamlforge/blob/main/LICENSE"><img src="../assets/GPL-3.0License.svg" alt="License"></a>
  <a href="https://github.com/s0w0h/yamlforge/pulls"><img src="../assets/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
</p>

**YamlForge** 是一个轻量级的工具，用于从 YAML 配置文件中提取信息并使用 JavaScript 脚本进行处理。

## 特性

- **YAML 配置提取:** 从远程 YAML 文件中提取指定字段，生成 `.list` 文件。
- **JavaScript 脚本处理:** 支持使用 JavaScript 脚本对 YAML 配置进行修改和合并。
- **GitHub 集成:** 可将生成的 `.list` 文件自动上传到 GitHub 仓库。
- **简易网页访问:** 提供一个简单的网页界面，方便用户进行配置和操作。

## 使用指南--restart unless-stopped

### 1. 部署

#### Docker (推荐)

```bash
docker run -d --restart unless-stopped --name yamlforge -p 19527:19527 -e API_KEY=your_api_key s0w0h/yamlforge:latest
```

`-e API_KEY=your_api_key`用于设置 API 密钥，可以使用逗号分隔多个 API 密钥，例如 -e API_KEY=key1,key2,key3。

#### 自行构建 Docker 镜像

1. 克隆仓库:
   ```bash
   git clone https://github.com/s0w0h/yamlforge.git
   ```
2. 修改 `Dockerfile`
   设置API_KEY
3. 构建镜像:
   ```bash
   cd yamlforge
   docker build -t yamlforge .
   ```
4. 运行容器:
   ```bash
   docker run -d --restart unless-stopped --name yamlforge -p 19527:19527 -e API_KEY=your_api_key yamlforge
   ```

#### 直接运行 (Python 3.9)

1. 克隆仓库:
   ```bash
   git clone https://github.com/s0w0h/yamlforge.git
   ```
2. 安装依赖:
   ```bash
   cd yamlforge
   pip install -r requirements.txt
   npm install js-yaml iconv-lite
   ```
3. 设置环境变量:
   ```bash
   export API_KEY=your_api_key
   ```
4. 运行应用:
   ```bash
   python app.py
   ```

### 2. API 接口

应用运行后，可以通过以下 API 接口进行操作:

- **`/listget`:** 提取 YAML 字段列表并生成 `.list` 文件。
- **`/yamlprocess`:** 使用 JavaScript 脚本处理 YAML 配置。

#### `/listget` 参数说明

| 参数                | 说明                                                                             | 是否必需 | 默认值                |
| ------------------- | -------------------------------------------------------------------------------- | -------- | --------------------- |
| `api_key`         | API 密钥                                                                         | 是       |                       |
| `source`          | YAML 文件的 URL，**注意，为了防止出现意想不到的问题，建议进行URL encode** | 是       |                       |
| `proxy`           | 下载YAML文件使用的代理配置，格式: http://user:pass@host:port 或 socks5://host:port| 否       |                       |
| `field`           | 需要提取的字段 (当 `resolve_domains` 为 `false` 时生效)                      | 否       | `general.name`      |
| `repo`            | GitHub 仓库名称 (格式:`username/repo`)                                         | 否       |                       |
| `token`           | GitHub 个人访问令牌                                                              | 否       |                       |
| `branch`          | GitHub 分支名称                                                                  | 否       | `main`              |
| `path`            | GitHub 仓库中的文件路径                                                          | 否       | 根目录                |
| `filename`        | 生成的文件名                                                                     | 否       | `yaml.list`         |
| `dns_servers`     | 用逗号分隔的 DNS 服务器列表 (当 `resolve_domains` 为 `true` 时生效)          | 否       | `223.5.5.5,8.8.8.8` |
| `max_depth`       | 字段或域名解析解析的最大深度                                                     | 否       | `8`                 |
| `resolve_domains` | 是否解析域名 (如果为 `true`，则会自动提取yaml配置中服务器地址并解析域名)       | 否       | `false`             |

**示例:**

```
http://IP:PORT/listget?api_key=your_api_key&source=YOUR_YAML_URL&field=YOUR_YAML_FIELD&repo=YOUR_REPO_NAME&token=YOUR_GITHUB_TOKEN&branch=YOUR_BRANCH_NAME&path=YOUR_PATH&filename=YOUR_FILE_NAME.list&dns_servers=223.5.5.5,119.29.29.29,1.1.1.1,8.8.8.8&max_depth=10&resolve_domains=true
```

#### `/yamlprocess` 参数说明

| 参数         | 说明                                                                                                  | 是否必需 | 默认值             |
| ------------ | ----------------------------------------------------------------------------------------------------- | -------- | ------------------ |
| `api_key`  | API 密钥                                                                                              | 是       |                    |
| `source`   | 基础 YAML 配置文件的 URL，**注意，为了防止出现意想不到的问题，建议进行URL encode**             | 是       |                    |
| `merge`    | 用于合并配置的 JavaScript 脚本的 URL，**注意，为了防止出现意想不到的问题，建议进行URL encode** | 是       |                    |
| `filename` | 生成的文件名                                                                                          | 否       | 与 `source` 相同 |
| `proxy`    | 下载文件使用的代理配置，格式: http://user:pass@host:port 或 socks5://host:port| 否       |                       |

**示例:**

```
http://IP:PORT/yamlprocess?api_key=your_api_key&source=YOUR_BASE_YAML_URL&merge=YOUR_MERGE_JS_URL&filename=YOUR_FILE_NAME
```

#### JavaScript 脚本说明

JavaScript 脚本需要定义一个 `main` 函数，该函数接收一个 JSON 对象作为参数，并返回处理后的 JSON 对象。

### 3. 简易网页访问

应用运行后，可以通过 `http://IP:19527` 访问一个简单的网页界面，实现了绝大部分功能。

## 安全提示

- 在公网部署时，强烈建议设置 API 密钥，防止 API 接口被滥用。
- 在生产环境中使用 HTTPS 保护 API 通信。
- 不要泄露 GitHub 个人访问令牌。
- 建议自行部署 YamlForge，避免使用不明来源的转换网站，防止配置信息泄露。

## 免责声明

本项目仅供学习和研究使用，请勿用于非法用途。

## 许可协议

[GPLv3](LICENSE)
