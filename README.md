# MFA Known Question from client_id for Whatsapp/Chat Bots

This repository contains a Python script for implementing Multi-Factor Authentication (MFA) using known questions from a client_id for WhatsApp/Chat Bots. This script allows you to generate dynamic web pages with questions for users to answer, validate their responses, and redirect them to a WhatsApp deep link for further interaction.

## Configuration

Before running the script, you need to configure the following variables:

- `HOST`: The server host (Replace with the server you are hosting with).
- `URL_SUFFIX`: The URL suffic to access the server (e.g., "http://" or "https://").
- `expiration`: Time in seconds to delete dynamically generated pages.
- `VALIDATION_API_URL`: The URL of an external validation API if you want to pre-validate answers.
- `api_port`: The port for API server. Here you receive client_id and question to be served.
- `web_port`: The port for the web server you will get to redirect your whatsapp/chat to respond known question.

## Dependencies

Ensure you have Python installed on your system. You can install the required Python libraries using pip:

```
pip install fastapi uvicorn waitress flask requests
```

## Running the Script

To run the script, execute the following command:

```
python mnMFA.py
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
   docker run -p 80:80 -p 8000:8000 mn_mfa
   ```

The script will be accessible through ports 80 and 8000 on your localhost.

## Usage

Once the script is running, you can access the dynamically generated pages by visiting the URLs provided by the API. Users can answer the questions, and their responses will be validated and redirected to a WhatsApp deep link for further action.

## HTTPS
`Generate Self-Signed Certificates:`

You can use OpenSSL to generate self-signed certificates. Run the following commands to generate a private key and a self-signed certificate:

```
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

This command will generate a certificate (cert.pem) and a private key (key.pem) valid for 365 days. Follow the prompts to fill in details like country, organization, etc.

You can then change the uvicorn line to work like this:
```
threading.Thread(target=lambda: uvicorn.run(fast_app, host=HOST, port=api_p, ssl_keyfile="key.pem", ssl_certfile="cert.pem">
```
## Enjoy!

With Whatsapp not being able to MFA certain questions and being able to authenticate with systems, this MFA solution is valid as an MFA as long as you can:
1. Call from your whatsapp/chatbot logic the API (in https://) where you supply the clientID and question to be asked.
2. You can the modify the validate_answer() method to call a webhook back with the right answer, and then just redirect to whatsapp conversation with you having the control back at the server.
3. The demo just returns the answer to Whatsapp (not using validate_answer() for demo purposes). Do not do this as people could scroll and see answers in chat (disappearing messages are not good in Whatsapp)

Enjoy!
Marvin Nahmias

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
