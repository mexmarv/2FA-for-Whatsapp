# 使用 Chatfuel（如果需要）的 Whatsapp/聊天機器人的 2FA 以及來自 client_id 的已知答案

此儲存庫包含用於使用 WhatsApp/聊天機器人的 client_id 的已知答案（出生日期）實現雙重認證 (2FA) 的 Python 程式碼。該專案允許您生成動態網頁，其中包含問題供用戶回答，驗證他們的回應，並將其重定向到 WhatsApp 深層連結以進行進一步交互，同時響應 chatfuel 以驗證用戶是否獲得所需的流量或區塊。您可以從此儲存庫中學習並進行相應的整合。

[![dependency - Python](https://img.shields.io/badge/dependency-Python-blue)](https://pypi.org/project/Python)![GitHub language count](https://img.shields.io/github/languages/count/mexmarv/2FA-for-Whatsapp)![GitHub commit activity](https://img.shields.io/github/commit-activity/y/mexmarv/2FA-for-Whatsapp)[![License](https://img.shields.io/badge/License-MIT-blue)](#license)[![issues - 2FA-for-Whatsapp](https://img.shields.io/github/issues/mexmarv/2FA-for-Whatsapp)](https://github.com/mexmarv/2FA-for-Whatsapp/issues)

## 配置

在運行腳本之前，需要配置以下變數：

-   `HOST`：伺服器主機（替換為您託管的伺服器）。
-   `URL_SUFFIX`：足以存取伺服器的 URL（例如“http&#x3A;//”或“https&#x3A;//”，但建議使用 https，因為 Whatsapp 和 Google 重定向到安全性）。
-   `expiration`：刪除動態產生的頁面的時間（以秒為單位）。
-   `api_port`：API伺服器的連接埠。在這裡您會收到 client_id 和要服務的問題。
-   `web_port`：網頁伺服器的端口，您將重新導向您的 Whatsapp/聊天以回答已知問題。

## 依賴關係

確保您的系統上安裝了 Python。您可以使用 pip3 安裝所需的 Python 函式庫：

    pip3 install fastapi uvicorn waitress flask requests sqlite3

或者

    pip install -r requirements.txt

## 運行腳本

若要執行該腳本，請執行以下命令：

    python3 mnMFA.py

該腳本將啟動 API 和 Web 伺服器執行緒來處理動態頁面產生和驗證。

## Docker安裝

Alternatively, you can run the script within a Docker container. Follow these steps:

1.  建置 Docker 映像：

        docker build -t mn_mfa .

2.  運行 Docker 容器：

        docker run -p 443:443 -p 8000:8000 mn_mfa

可以透過本機主機上的連接埠 443 和 8000 存取該伺服器。

## HTTPS（需要）

`Generate Self-Signed Certificates:`

您可以使用 OpenSSL 產生自簽名憑證。執行以下命令產生私鑰和自簽名憑證：

    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

此命令將產生一個憑證（cert.pem）和一個有效期為 365 天的私鑰（key.pem）。依照提示填寫國家、組織等詳細資料。

您始終可以從許多供應商獲得 90 天的免費 SSL，但需要安裝金鑰和憑證。

## 用法

腳本運行後，您可以透過造訪 API 提供的 URL 來存取動態產生的頁面。用戶可以從兩個隨機生成器中回答多個答案，他們的回答將被驗證，發送回 Chatfuel，並重定向到 WhatsApp 深層鏈接，以便在聊天機器人響應時採取進一步行動。

此外，對於每個成功的答案，時間戳記和 IP 位址以及其他資料都保存在「logs.db」中，如果用戶聲明他沒有進行交易，您可以使用它來幫助您獲得他正確回答的資訊IP 和一些額外的數據。對於某些法律的不可否認性，這個資料庫有幫助。

## 筆記：

由於 Whatsapp 無法對某些問題進行 MFA 且無法通過系統進行身份驗證，因此只要您能夠滿足以下條件，此 MFA 解決方案就作為 MFA 有效：

1.  在 chatfuel 中產生一個工作流程，驗證使用者的某些交易。附有範例工作流程。
    <center><img src="/chatfuel.png"/></center>
2.  Reading through code is easy, you can integrate back with any external API to make use of answers and trasnactions. I generated this simple System Diagram for understanding (thanks to AI/GPT for the help from my input).
    <center><img src="/2FASystemDiagram.svg"/></center>
3.  不要透過聊天管道返回答案，這違背了 2FA 的目的。
4.  我添加了`loadtest.py`為了好玩，您可以使用盡可能多的請求和執行緒進行負載測試來測試您的 Docker 或生產環境。我禁用了憑證 SSL 檢查，因為這需要太多時間來驗證。在 docker 中執行最新 Ubuntu 的 1 CPU、8 GB RAM Docker 實例中出現一些有趣的結果：


    10,000 tries with 1000 threads. Running on Docker, no certificate checking.
    Total time taken: 6.910074949264526 seconds
    Total successful requests: 10,000
    Total errors: 0
    Total requests: 10,000
    Transactions per second (TPS): 204.7162306258972

享受！
馬文·納米亞斯

## 執照

發佈於[和](/LICENSE)經過[@mexmarv](https://github.com/mexmarv).
