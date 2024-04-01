# 2FA for Whatsapp/Chatbots using Chatfuel (if needed) and known answers from client_id

This repository contains Pythn code for implementing Two-Factor Authentication (2FA) using known answer (birth date) from a client_id for WhatsApp/Chat Bots. This project allows you to generate dynamic web pages with questions for users to answer, validate their responses, and redirect them to a WhatsApp deep link for further interaction, while responding back to chatfuel to validate the user for the desired flow or block. You can learn from this repository and integrate accordingly.

[![dependency - Python](https://img.shields.io/badge/dependency-Python-blue)](https://pypi.org/project/Python)
[![GitHub tag](https://img.shields.io/github/tag/mexmarv/2FA-for-Whatsapp?include_prereleases=&sort=semver&color=blue)](https://github.com/mexmarv/2FA-for-Whatsapp/releases/)
[![License](https://img.shields.io/badge/License-MIT-blue)](#license)
[![issues - 2FA-for-Whatsapp](https://img.shields.io/github/issues/mexmarv/2FA-for-Whatsapp)](https://github.com/mexmarv/2FA-for-Whatsapp/issues)

## Configuration

Before running the script, you need to configure the following variables:

- `HOST`: The server host (Replace with the server you are hosting with).
- `URL_SUFFIX`: The URL suffic to access the server (e.g., "http://" or "https://", but suggest https since Whatsapp and Google redirect to security).
- `expiration`: Time in seconds to delete dynamically generated pages.
- `api_port`: The port for API server. Here you receive client_id and question to be served.
- `web_port`: The port for the web server you will get to redirect your whatsapp/chat to respond known question.

## Dependencies

Ensure you have Python installed on your system. You can install the required Python libraries using pip3:

```
pip3 install fastapi uvicorn waitress flask requests sqlite3
```
or 
```
pip install -r requirements.txt
```

## Running the Script

To run the script, execute the following command:

```
python3 mnMFA.py
```

The script will start both API and web server threads to handle dynamic page generation and validation.

## Docker Installation

Alternatively, you can run the script within a Docker container. Follow these steps:

1. Build the Docker image:

   ```
   docker build -t mn_mfa .
   ```

2. Run the Docker container:

   ```
   docker run -p 443:443 -p 8000:8000 mn_mfa
   ```

The server will be accessible through ports 443 and 8000 on your localhost.

## HTTPS (Needed)
`Generate Self-Signed Certificates:`

You can use OpenSSL to generate self-signed certificates. Run the following commands to generate a private key and a self-signed certificate:

```
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

This command will generate a certificate (cert.pem) and a private key (key.pem) valid for 365 days. Follow the prompts to fill in details like country, organization, etc.

You can always get free SSLs for 90 days from many venders, but both the key and cert neeed to be installed.

## Usage

Once the script is running, you can access the dynamically generated pages by visiting the URLs provided by the API. Users can answer the multiple answers form two random generators, and their responses will be validated, sent back to Chatfuel, and redirected to a WhatsApp deep link for further action as your chatbot responds.

Also, for every successful answer, the timestamp and IP adress with other data is saved in ´logs.db´, which you can use to help if a user states that he did not do the transaction, you have information he answer correctly forn an IP and some extra data. Non repudiation for certain laws, this DB helps.

## Notes:
With Whatsapp not being able to MFA certain questions and being able to authenticate with systems, this MFA solution is valid as an MFA as long as you can:
1. Generate a workflow in chatfuel that validates the user for certain transactions. An example workflow is attached.
   <center><img src="/chatfuel.png"/></center>
2. Reading through code is easy, you can integrate back with any external API to make use of answers and trasnactions.
3. Do not return the answers through the chat channel, this defeats the purpose of 2FA.
4. I added `loadtest.py` which for fun you can loadtest with as many requests and threads to test your Docker or production environment. I disabled certificate SSL checking as this takes too much time to validate. Some interesting results in a 1 CPU, 8 GB RAM Docker Instance runing latest Ubuntu in docker:
```
10,000 tries with 1000 threads. Running on Docker, no certificate checking.
Total time taken: 6.910074949264526 seconds
Total successful requests: 10,000
Total errors: 0
Total requests: 10,000
Transactions per second (TPS): 204.7162306258972
```

Enjoy!
Marvin Nahmias

## License

Released under [MIT](/LICENSE) by [@mexmarv](https://github.com/mexmarv).
