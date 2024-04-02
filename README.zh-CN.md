# 使用 Chatfuel（如果需要）的 Whatsapp/聊天机器人的 2FA 以及来自 client_id 的已知答案

此存储库包含用于使用 WhatsApp/聊天机器人的 client_id 的已知答案（出生日期）实现双因素身份验证 (2FA) 的 Python 代码。该项目允许您生成动态网页，其中包含问题供用户回答，验证他们的响应，并将其重定向到 WhatsApp 深层链接以进行进一步交互，同时响应 chatfuel 以验证用户是否获得所需的流量或块。您可以从此存储库中学习并进行相应的集成。

[![dependency - Python](https://img.shields.io/badge/dependency-Python-blue)](https://pypi.org/project/Python)![GitHub language count](https://img.shields.io/github/languages/count/mexmarv/2FA-for-Whatsapp)![GitHub commit activity](https://img.shields.io/github/commit-activity/y/mexmarv/2FA-for-Whatsapp)[![License](https://img.shields.io/badge/License-MIT-blue)](#license)[![issues - 2FA-for-Whatsapp](https://img.shields.io/github/issues/mexmarv/2FA-for-Whatsapp)](https://github.com/mexmarv/2FA-for-Whatsapp/issues)

## 配置

运行脚本之前，需要配置以下变量：

-   `HOST`：服务器主机（替换为您托管的服务器）。
-   `URL_SUFFIX`：足以访问服务器的 URL（例如“http&#x3A;//”或“https&#x3A;//”，但建议使用 https，因为 Whatsapp 和 Google 重定向到安全）。
-   `expiration`：删除动态生成的页面的时间（以秒为单位）。
-   `api_port`：API服务器的端口。在这里您会收到 client_id 和要服务的问题。
-   `web_port`：网络服务器的端口，您将重定向您的 Whatsapp/聊天以回答已知问题。

## 依赖关系

确保您的系统上安装了 Python。您可以使用 pip3 安装所需的 Python 库：

    pip3 install fastapi uvicorn waitress flask requests sqlite3

或者

    pip install -r requirements.txt

## 运行脚本

要运行该脚本，请执行以下命令：

    python3 mnMFA.py

该脚本将启动 API 和 Web 服务器线程来处理动态页面生成和验证。

## Docker安装

或者，您可以在 Docker 容器中运行该脚本。按着这些次序：

1.  构建 Docker 镜像：

        docker build -t mn_mfa .

2.  运行 Docker 容器：

        docker run -p 443:443 -p 8000:8000 mn_mfa

可以通过本地主机上的端口 443 和 8000 访问该服务器。

## HTTPS（需要）

`Generate Self-Signed Certificates:`

您可以使用 OpenSSL 生成自签名证书。运行以下命令生成私钥和自签名证书：

    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

此命令将生成一个证书（cert.pem）和一个有效期为 365 天的私钥（key.pem）。按照提示填写国家、组织等详细信息。

您始终可以从许多供应商处获得 90 天的免费 SSL，但需要安装密钥和证书。

## 用法

脚本运行后，您可以通过访问 API 提供的 URL 来访问动态生成的页面。用户可以从两个随机生成器中回答多个答案，他们的回答将被验证，发送回 Chatfuel，并重定向到 WhatsApp 深层链接，以便在聊天机器人响应时采取进一步行动。

此外，对于每个成功的答案，时间戳和 IP 地址以及其他数据都保存在“logs.db”中，如果用户声明他没有进行交易，您可以使用它来帮助您获得他正确回答的信息IP 和一些额外的数据。对于某些法律的不可否认性，这个数据库有帮助。

## 笔记：

由于 Whatsapp 无法对某些问题进行 MFA 且无法通过系统进行身份验证，因此只要您能够满足以下条件，此 MFA 解决方案就作为 MFA 有效：

1.  在 chatfuel 中生成一个工作流程，验证用户的某些交易。附有示例工作流程。
    <center><img src="/chatfuel.png"/></center>
2.  阅读代码很容易，您可以与任何外部 API 重新集成以利用答案和交易。我生成了这个简单的系统图以供理解（感谢 AI/GPT 对我的输入的帮助）。
    <center><img src="/2FASystemDiagram.svg"/></center>
3.  不要通过聊天渠道返回答案，这违背了 2FA 的目的。
4.  我添加了`loadtest.py`为了好玩，您可以使用尽可能多的请求和线程进行负载测试来测试您的 Docker 或生产环境。我禁用了证书 SSL 检查，因为这需要太多时间来验证。在 docker 中运行最新 Ubuntu 的 1 CPU、8 GB RAM Docker 实例中出现一些有趣的结果：


    10,000 tries with 1000 threads. Running on Docker, no certificate checking.
    Total time taken: 6.910074949264526 seconds
    Total successful requests: 10,000
    Total errors: 0
    Total requests: 10,000
    Transactions per second (TPS): 204.7162306258972

享受！
马文·纳米亚斯

## 执照

发布于[和](/LICENSE)经过[@mexmarv](https://github.com/mexmarv).
