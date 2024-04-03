# 2FA pour Whatsapp/Chatbots utilisant Chatfuel (si nécessaire) et réponses connues de client_id

Ce référentiel contient du code Python pour la mise en œuvre de l'authentification à deux facteurs (2FA) à l'aide d'une réponse connue (date de naissance) d'un client_id pour WhatsApp/Chat Bots. Ce projet vous permet de générer des pages Web dynamiques avec des questions auxquelles les utilisateurs doivent répondre, de valider leurs réponses et de les rediriger vers un lien profond WhatsApp pour une interaction ultérieure, tout en répondant à chatfuel pour valider l'utilisateur pour le flux ou le blocage souhaité. Vous pouvez apprendre de ce référentiel et intégrer en conséquence.

[![dependency - Python](https://img.shields.io/badge/dependency-Python-blue)](https://pypi.org/project/Python)![GitHub language count](https://img.shields.io/github/languages/count/mexmarv/2FA-for-Whatsapp)![GitHub commit activity](https://img.shields.io/github/commit-activity/y/mexmarv/2FA-for-Whatsapp)[![License](https://img.shields.io/badge/License-MIT-blue)](#license)[![issues - 2FA-for-Whatsapp](https://img.shields.io/github/issues/mexmarv/2FA-for-Whatsapp)](https://github.com/mexmarv/2FA-for-Whatsapp/issues)

## Configuration

Avant d'exécuter le script, vous devez configurer les variables suivantes :

-   `HOST`: L'hôte du serveur (remplacez par le serveur avec lequel vous hébergez).
-   `URL_SUFFIX`: L'URL suffit pour accéder au serveur (par exemple, "http&#x3A;//" ou "https&#x3A;//", mais suggère https puisque Whatsapp et Google redirigent vers la sécurité).
-   `expiration`: Temps en secondes pour supprimer les pages générées dynamiquement.
-   `api_port`: Le port du serveur API. Ici, vous recevez client_id et la question à répondre.
-   `web_port`: Le port du serveur Web que vous obtiendrez pour rediriger votre WhatsApp/chat pour répondre à une question connue.

## Dépendances

Assurez-vous que Python est installé sur votre système. Vous pouvez installer les bibliothèques Python requises à l'aide de pip3 :

    pip3 install fastapi uvicorn waitress flask requests sqlite3

ou

    pip install -r requirements.txt

## Exécuter le script

Pour exécuter le script, exécutez la commande suivante :

    python3 mnMFA.py

Le script démarrera les threads de l'API et du serveur Web pour gérer la génération et la validation de pages dynamiques.

## Installation du menu Docker

Vous pouvez également exécuter le script dans un conteneur Docker. Suivez ces étapes:

1.  Créez l'image Docker :

        docker build -t mn_mfa .

2.  Exécutez le conteneur Docker :

        docker run -p 443:443 -p 8000:8000 mn_mfa

Le serveur sera accessible via les ports 443 et 8000 sur votre hôte local.

## HTTPS (obligatoire)

`Generate Self-Signed Certificates:`

Vous pouvez utiliser OpenSSL pour générer des certificats auto-signés. Exécutez les commandes suivantes pour générer une clé privée et un certificat auto-signé :

    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

Cette commande générera un certificat (cert.pem) et une clé privée (key.pem) valables 365 jours. Suivez les invites pour renseigner des détails tels que le pays, l'organisation, etc.

Vous pouvez toujours obtenir un SSL gratuit pendant 90 jours auprès de nombreux fournisseurs, mais la clé et le certificat doivent être installés.

## Usage

Une fois le script exécuté, vous pouvez accéder aux pages générées dynamiquement en visitant les URL fournies par l'API. Les utilisateurs peuvent répondre aux multiples réponses à partir de deux générateurs aléatoires, et leurs réponses seront validées, renvoyées à Chatfuel et redirigées vers un lien profond WhatsApp pour une action ultérieure à mesure que votre chatbot répond.

Also, for every successful answer, the timestamp and IP adress with other data is saved in ´logs.db´, which you can use to help if a user states that he did not do the transaction, you have information he answer correctly forn an IP and some extra data. Non repudiation for certain laws, this DB helps.

## Remarques:

Whatsapp ne pouvant pas répondre à certaines questions par MFA et ne pouvant pas s'authentifier auprès des systèmes, cette solution MFA est valable en tant que MFA tant que vous le pouvez :

1.  Générez un workflow dans chatfuel qui valide l'utilisateur pour certaines transactions. Un exemple de flux de travail est joint.
    <center><img src="/chatfuel.png"/></center>
2.  La lecture du code est facile, vous pouvez réintégrer n'importe quelle API externe pour utiliser les réponses et les transactions. J'ai généré ce diagramme système simple pour comprendre (merci à AI/GPT pour l'aide de ma contribution).
    <center><img src="/2FASystemDiagram.svg"/></center>
3.  Ne renvoyez pas les réponses via le canal de discussion, cela va à l’encontre de l’objectif de 2FA.
4.  J'ai ajouté`loadtest.py`que, pour le plaisir, vous pouvez charger avec autant de requêtes et de threads pour tester votre Docker ou votre environnement de production. J'ai désactivé la vérification du certificat SSL car la validation prend trop de temps. Quelques résultats intéressants dans une instance Docker de 1 processeur et 1 Go de RAM exécutant la dernière version d'Ubuntu dans Docker :


    10,000 tries with 1000 threads. Running on Docker, no certificate checking.
    Total time taken: 6.910074949264526 seconds
    Total successful requests: 10,000
    Total errors: 0
    Total requests: 10,000
    Transactions per second (TPS): 204.7162306258972

Apprécier!
Marvin Nahmias

## Licence

Publié sous[AVEC](/LICENSE)par[@mexmarv](https://github.com/mexmarv).
