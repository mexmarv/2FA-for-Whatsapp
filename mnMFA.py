##############################################################
# MFA Known Question from client_id for Whatsapp/Chat Bots   #
# Marvin Nahmias, 2024.                                      #
##############################################################

import string, time, threading, requests, random, uvicorn
from waitress import serve
from flask import Flask, render_template, request, redirect
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse

# Server (Replace with the server you are hosting with if you like)
HOST = "0.0.0.0" # localhost
URL_SUFFIX = "http://" + HOST

# Seconds to delete dynamic generated pages (ex: 300 = 5 min)
expiration = 20
# Dictionary to store dynamic web pages and their expiration times in memory
dynamic_pages = {}
# Ports
web_port = 80
api_port = 8000
# Apps
fast_app = FastAPI()
web_app = Flask(__name__,
    template_folder='./',
    static_folder='./')
web_app.config['CORS_HEADERS'] = 'Content-Type'
# HTML Header & Footer
header = f"""
    <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Pregunta Dinámica</title>
                <!-- Bootstrap CSS -->
                <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>"""

footer = f"""
            <!-- Bootstrap JS -->
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.bundle.min.js"></script>
            <script type="text/javascript">
                var timeleft = {expiration};
                var downloadTimer = setInterval(function(){{
                    timeleft--;
                    document.getElementById("countdowntimer").textContent = timeleft + " seg";
                if(timeleft <= 0)
                clearInterval(downloadTimer);
            	}},1000);
            </script>
            </body>
            </html>"""

def generate_dynamic_page(client_id, pregunta):
    # Generate dynamic web page HTML using bootstrap CDN
    dynamic_page = f"""
	        <div class="container mt-5">
            <center>
	        <img class="img-fluid" width="300" src="https://cdn-icons-png.flaticon.com/512/7380/7380525.png">
     	    	</br></br>
            </center>
	        <h3>Please answer in <span id="countdowntimer" class="badge badge-secondary">{expiration} seg</span></h3>
            <div class="alert alert-primary" role="alert">{pregunta}</div>
            <form method="post" action="/validate_answer">
                <input type="hidden" id="client_id" name={client_id}>
                <div class="form-group">
                        <label for="answer">Your answer:</label>
                        <input type="text" class="form-control" id="respuesta" name="respuesta" required>
                </div>
                </br>
		    <button type="submit" class="btn btn-primary">Submit</button>
            </form>"""
    
    return (header + dynamic_page + footer)

def validate_answer(client_id, respuesta):
    # TODO: if you want to prevalidate answer: Call the external validation API
    response = requests.post(VALIDATION_API_URL, json={"client_id": client_id, "respuesta": respuesta})
    if response.status_code == 200:
        return response.json().get("correct", False)
    return False

def clear_expired_pages():
    while True:
        current_time = time.time()
        try:
            expired_pages = [page_id for page_id in dynamic_pages if dynamic_pages[page_id]['expiration_time'] < current_time]
            for page_id in expired_pages:
                del dynamic_pages[page_id]
                print(f"--- Deleted: {page_id}")
        except:
            print("--- Dynamic Array resized.")

        time.sleep(expiration - 5)  # Check every expiration time - 5 seconds.

@fast_app.get('/generate_dynamic_page')
async def generate_dynamic_page_api(client_id: str, pregunta: str):
    if not client_id:
        raise HTTPException(status_code=400, detail="Client ID is required")
    # Generate dynamic web page
    dynamic_page = generate_dynamic_page(client_id, pregunta)
    if dynamic_page:
        # Generate unique page ID
        page_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        # Set expiration time for expiration time from now
        expiration_time = time.time() + expiration
        dynamic_pages[page_id] = {'content': dynamic_page, 'expiration_time': expiration_time}
        return {"dynamic_url": f"{URL_SUFFIX}/{page_id}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate dynamic page.")

@web_app.route('/<page_id>')
def dynamic_page(page_id):
    if page_id in dynamic_pages:
        return dynamic_pages[page_id]['content']
    else:
        return (header + """
                <div class="row justify-content-md-center">
                <div class="col-12 col-md-11 col-lg-9 col-xl-7 col-xxl-6 text-center text-black"></br>
                <h2 class="display-3 fw-bold mb-3">Dynamic page not found.</h2></div></div>""" + footer)

@web_app.route('/validate_answer', methods=['POST'])
def validate_answer_api():
    client_id = request.form.get("client_id")
    respuesta = request.form.get("respuesta")

    # Validate the answer
    # is_correct = validate_answer(field, answer)

    # Redirect to a WhatsApp deep link
    phone_number = "+525541637703"  # Replace with your phone number
    # urespuesta = respuesta.encode("utf-8")
    whatsapp_url = f"https://wa.me/{phone_number}?text=Respuesta: {respuesta}"
    return redirect(whatsapp_url)

@web_app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print("\n\n\n....: MFA : Starting expired pages thread ...")
    threading.Thread(target=clear_expired_pages, daemon=True).start()
    print(f"....: MFA : Starting API service thread ({api_port})...")
    threading.Thread(target=lambda: uvicorn.run(fast_app, host=HOST, port=api_port)).start()
    print(f"....: MFA : Starting WEB service thread ({web_port})...\n")
    serve(web_app, host=HOST, port=web_port)
    print("... Enter another control-C to close.")
