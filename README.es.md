# 2FA para Whatsapp/Chatbots usando Chatfuel (si es necesario) y respuestas conocidas de client_id

Este repositorio contiene código Python para implementar la autenticación de dos factores (2FA) utilizando una respuesta conocida (fecha de nacimiento) de un client_id para WhatsApp/Chat Bots. Este proyecto le permite generar páginas web dinámicas con preguntas para que los usuarios respondan, validar sus respuestas y redirigirlas a un enlace profundo de WhatsApp para una mayor interacción, mientras responde a chatfuel para validar al usuario para el flujo o bloque deseado. Puede aprender de este repositorio e integrarlo en consecuencia.

[![dependency - Python](https://img.shields.io/badge/dependency-Python-blue)](https://pypi.org/project/Python)![GitHub language count](https://img.shields.io/github/languages/count/mexmarv/2FA-for-Whatsapp)![GitHub commit activity](https://img.shields.io/github/commit-activity/y/mexmarv/2FA-for-Whatsapp)[![License](https://img.shields.io/badge/License-MIT-blue)](#license)[![issues - 2FA-for-Whatsapp](https://img.shields.io/github/issues/mexmarv/2FA-for-Whatsapp)](https://github.com/mexmarv/2FA-for-Whatsapp/issues)

## Configuración

Antes de ejecutar el script, debe configurar las siguientes variables:

-   `HOST`: El host del servidor (Reemplace con el servidor con el que está hospedando).
-   `URL_SUFFIX`: La URL es suficiente para acceder al servidor (por ejemplo, "http&#x3A;//" o "https&#x3A;//", pero sugiere https ya que Whatsapp y Google redirigen a seguridad).
-   `expiration`: Tiempo en segundos para eliminar páginas generadas dinámicamente.
-   `api_port`: El puerto para el servidor API. Aquí recibe client_id y la pregunta para ser atendida.
-   `web_port`: El puerto para el servidor web al que podrá redirigir su WhatsApp/chat para responder preguntas conocidas.

## Dependencias

Asegúrese de tener Python instalado en su sistema. Puede instalar las bibliotecas de Python necesarias usando pip3:

    pip3 install fastapi uvicorn waitress flask requests sqlite3

o

    pip install -r requirements.txt

## Ejecutando el guión

Para ejecutar el script, ejecute el siguiente comando:

    python3 mnMFA.py

El script iniciará subprocesos de API y del servidor web para manejar la generación y validación dinámica de páginas.

## Instalación de ventana acoplable

Alternativamente, puede ejecutar el script dentro de un contenedor Docker. Sigue estos pasos:

1.  Construya la imagen de Docker:

        docker build -t mn_mfa .

2.  Ejecute el contenedor Docker:

        docker run -p 443:443 -p 8000:8000 mn_mfa

Se podrá acceder al servidor a través de los puertos 443 y 8000 en su host local.

## HTTPS (necesario)

`Generate Self-Signed Certificates:`

Puede utilizar OpenSSL para generar certificados autofirmados. Ejecute los siguientes comandos para generar una clave privada y un certificado autofirmado:

    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

Este comando generará un certificado (cert.pem) y una clave privada (key.pem) válida por 365 días. Siga las instrucciones para completar detalles como país, organización, etc.

Siempre puede obtener SSL gratuito durante 90 días de muchos proveedores, pero es necesario instalar tanto la clave como el certificado.

## Uso

Una vez que se ejecuta el script, puede acceder a las páginas generadas dinámicamente visitando las URL proporcionadas por la API. Los usuarios pueden responder las múltiples respuestas de dos generadores aleatorios, y sus respuestas serán validadas, enviadas de regreso a Chatfuel y redirigidas a un enlace profundo de WhatsApp para realizar más acciones a medida que su chatbot responde.

Además, por cada respuesta exitosa, la marca de tiempo y la dirección IP con otros datos se guardan en ´logs.db´, que puede usar para ayudar si un usuario afirma que no realizó la transacción, tiene información de que respondió correctamente para una IP y algunos datos extra. No repudio a ciertas leyes, esta BD ayuda.

## Notas:

Dado que Whatsapp no ​​puede realizar ciertas preguntas con MFA y puede autenticarse con sistemas, esta solución MFA es válida como MFA siempre que pueda:

1.  Generar un flujo de trabajo en chatfuel que valide al usuario para determinadas transacciones. Se adjunta un flujo de trabajo de ejemplo.
    <center><img src="/chatfuel.png"/></center>
2.  Leer el código es fácil, puede volver a integrarlo con cualquier API externa para utilizar respuestas y transacciones. Generé este diagrama de sistema simple para comprenderlo (gracias a AI/GPT por la ayuda de mis aportes).
    <center><img src="/2FASystemDiagram.svg"/></center>
3.  No devuelva las respuestas a través del canal de chat, esto anula el propósito de 2FA.
4.  yo añadí`loadtest.py`que, por diversión, puede realizar pruebas de carga con tantas solicitudes e hilos para probar su Docker o su entorno de producción. Desactivé la verificación del certificado SSL porque lleva demasiado tiempo validarlo. Algunos resultados interesantes en una instancia Docker de 1 CPU y 1 GB de RAM ejecutando la última versión de Ubuntu en Docker:


    10,000 tries with 1000 threads. Running on Docker, no certificate checking.
    Total time taken: 6.910074949264526 seconds
    Total successful requests: 10,000
    Total errors: 0
    Total requests: 10,000
    Transactions per second (TPS): 204.7162306258972

¡Disfrutar!
Marvin Nahmias

## Licencia

Publicado bajo[CON](/LICENSE)por[@mexmarv](https://github.com/mexmarv).
