###############################################################
# 2FA Known Questions from client_id for Whatsapp/Chat Bots   #
# Marvin Nahmias, 2024.                                       #
###############################################################

import ssl, string, time, threading, requests, random, uvicorn, re, sqlite3
from datetime import datetime, timedelta
from werkzeug.serving import run_simple
from flask import Flask, render_template, request, redirect
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse

# Server (Replace with the server you are hosting with if you like)
HOST = "0.0.0.0" # localhost
URL_SUFFIX = "https://" + HOST
CHATFUEL_TOKEN = "YOUR TOKEM"
BOT_ID = "YOUR BOT ID"
# Seconds to delete dynamic generated pages (ex: 300 = 5 min)
expiration = 60
# Dictionary to store dynamic web pages and their expiration times in memory
dynamic_pages = {}

# Ports
web_port = 443
api_port = 8000

# Functions
header = """
    <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Pregunta Dinámica</title>
                <!-- Bootstrap CSS -->
                <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
                <!-- Bootstrap JS -->
                <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.bundle.min.js"></script>
            </head>
            <body>
     """

footer = """
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

ip_data_get = """
    <script>
        // Function to fetch IP address
        async function getIPAddress() {
            const response = await fetch('https://api.ipify.org?format=json');
            const data = await response.json();
            return data.ip;
        }

        // Function to fetch location data based on IP
        async function getLocation(ip) {
            const response = await fetch(`https://ipapi.co/${ip}/json/`);
            const data = await response.json();
            return data;
        }

        // Function to update the hidden field with IP and location data
        async function updateHiddenField() {
            try {
                const ip = await getIPAddress();
                const locationData = await getLocation(ip);

                // Example: Constructing a JSON string with IP and location data
                const blobData = JSON.stringify({
                    ip: ip,
                    city: locationData.city,
                    country: locationData.country_name,
                    latitude: locationData.latitude,
                    longitude: locationData.longitude
                });

                // Update the hidden field
                document.getElementById('refdata').value = blobData;
            } catch (error) {
                console.error('Error fetching IP and location:', error);
            }
        }
        // Call the update function when the page loads
        window.onload = updateHiddenField;
    </script>"""

def insert_log(entrada, telefono):
    # Connect to the database
    conn = sqlite3.connect('logs.db')
    c = conn.cursor()
    
    # Create table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS validation_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  telefono TEXT,
                  autorizacion BLOB)''')

    # Insert log into the database
    log_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    autorizacion = entrada.encode('utf-8')
    c.execute("INSERT INTO validation_logs (date, telefono, autorizacion) VALUES (?, ?, ?)", (log_date, telefono, autorizacion))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

def generate_dynamic_page(client_id, page_id, flow_name, pregunta, options, telefono):
    # Generate dynamic web page HTML using bootstrap CDN
    dynamic_page = f"""
	        <div class="container mt-5">
            <center>
	        <img class="img-fluid" width="300" src="https://cdn-icons-png.flaticon.com/512/7380/7380525.png">
     	    	</br></br>
            </center>
	        <h3>Por favor contesta en <span id="countdowntimer" class="badge badge-secondary">{expiration} seg.</span></h3>
            <div class="alert alert-primary" role="alert"><bold>{pregunta}</bold></div>
            <form method="post" action="/validate_answer">
                <input type="hidden" id="client_id" name="client_id" value="{client_id}">
                <input type="hidden" id="telefono" name="telefono" value="{telefono}">
                <input type="hidden" id="page_id" name="page_id" value="{page_id}">
                <input type="hidden" id="flow_name" name="flow_name" value="{flow_name}">
                <input type="hidden" id="refdata" name="refdata" value="">
                """
    dynamic_questions = cuatro_preguntas(pregunta, options) 
    
    dynamic_end = """
                </br>
		    <button type="submit" class="btn btn-primary">Mandar</button>
            </form>"""
    
    dynamic_page += header + dynamic_questions + dynamic_end + ip_data_get + footer
    
    return dynamic_page

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

        time.sleep(expiration + 1)  # Check expiration + 1 seg

def generate_birth_dates(correct_date):
    # Convert the correct date string to a datetime object
    correct_date = datetime.strptime(correct_date, '%Y-%m-%d')
    
    # Generate three random dates around the correct date (within a range of 60 days before or after)
    wrong_dates = []
    for _ in range(3):
        days_difference = random.randint(-60, 60)
        wrong_date = correct_date + timedelta(days=days_difference)
        # Ensure the wrong date is not the same as the correct date
        while wrong_date == correct_date:
            days_difference = random.randint(-10, 10)
            wrong_date = correct_date + timedelta(days=days_difference)
        wrong_dates.append(wrong_date.strftime('%Y-%m-%d'))
    
    # Add the correct date to the list of wrong dates
    all_dates = wrong_dates + [correct_date.strftime('%Y-%m-%d')]
    # Shuffle the list to randomize the order of dates
    random.shuffle(all_dates)
    
    return all_dates

def sum_date_digits(date):
    # Extract day and month from the date
    month, day = map(int, date.split('-')[1:])
    # Sum the digits of day and month separately
    return sum(map(int, str(month))) + sum(map(int, str(day)))

def sum_month_day(date):
    # Extract month and day from the date
    month, day = map(int, date.split('-')[1:])
    # Sum the entire numbers of month and day
    return month + day

def generate_sums(correct_date, possible_dates):
    # Calculate the sum of the correct date's digits
    correct_sum = sum_month_day(correct_date)
    
    # Generate three random sums
    wrong_sums = []
    while len(wrong_sums) < 3:
        random_sum = sum_date_digits(random.choice(possible_dates))
        # Ensure the random sum is not the same as the correct sum
        if random_sum != correct_sum and random_sum not in wrong_sums:
            wrong_sums.append(random_sum)
    
    # Add the correct sum to the list of wrong sums
    all_sums = wrong_sums + [correct_sum]
    
    # Shuffle the list to randomize the order of sums
    random.shuffle(all_sums)

    return all_sums

def cuatro_preguntas(question_text, options):
    html = """
    <div class="container">
        <div class="row">
            <div class="col">
              """
    
    for i, option in enumerate(options, start=1):
        html += f"""
                <div class="form-check">
                    <input class="form-check-input h5" type="radio" name="respuesta" id="q{i}_option" value="{option}">
                    <label class="form-check-label h5" for="q{i}_option">
                        {option}
                    </label>
                </div>"""
    
    html += """
            </div>
        </div>
    </div>
    """
    return html

# Apps
fast_app = FastAPI()
web_app = Flask(__name__)
web_app.config['CORS_HEADERS'] = 'Content-Type'

@fast_app.get('/generate_dynamic_page')

async def generate_dynamic_page_api(client_id: str, telefono: str, flow_name: str, fecha_cumple: str):
    if not client_id:
        raise HTTPException(status_code=400, detail="client_id is required")
    if not flow_name:
        raise HTTPException(status_code=400, detail="Flow Name is required")
    if not telefono:
        raise HTTPException(status_code=400, detail="Teléfono is required")
    if not fecha_cumple:
        raise HTTPException(status_code=400, detail="Cumpleaños is required")
    # Define a regular expression pattern for the desired date format
    date_pattern = re.compile(r'^\d{1,4}-\d{2}-\d{2}$')
    # Check if fecha_cumple matches the pattern
    if not date_pattern.match(fecha_cumple):
        raise HTTPException(status_code=400, detail="Fecha de cumpleaños must be in the format %Y-%m-%d")
    
    # Generate unique page ID (6 digits)
    page_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    sel_preguntas = random.randint(1, 2)  # Selecciona entre dos posibilidades de fecha_cumple
    possible_dates = generate_birth_dates(fecha_cumple)
    possible_sums = generate_sums(fecha_cumple, possible_dates)
    pregunta = ""
    respuestas = []

    if sel_preguntas == 1:
        pregunta = "¿Cuál es tu fecha de nacimiento?"
        possible_dates.append("Ninguna de las anteriores.")  # Añadir NDLA
        respuestas = possible_dates
        la_respuesta = fecha_cumple
    elif sel_preguntas == 2:
        pregunta = "¿Cuál es la suma del mes + día de tu cumpleaños (M+D)?"
        possible_sums.append("Ninguna de las anteriores.")  # Añadir NDLA
        respuestas = possible_sums
        la_respuesta = str(sum_month_day(fecha_cumple))

    dynamic_page = generate_dynamic_page(client_id, page_id, flow_name, pregunta, respuestas, telefono)
    
    if dynamic_page:
        # Set expiration time for expiration time from now
        expiration_time = time.time() + expiration
        dynamic_pages[page_id] = {'content': dynamic_page, 'expiration_time': expiration_time, 'respuesta': la_respuesta}
        return {"dynamic_url": f"{URL_SUFFIX}/{page_id}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate dynamic page.")

@web_app.route('/')
def index():
    return render_template('index.html')

@web_app.route('/<page_id>')
def dynamic_page(page_id):
    if page_id in dynamic_pages:
        return dynamic_pages[page_id]['content']
    else:
        return (header + """
                <div class="row justify-content-md-center">
                <div class="col-12 col-md-11 col-lg-9 col-xl-7 col-xxl-6 text-center text-black border border-danger"></br>
                <h3 class="display-3 fw-bold mb-3">Página dinámica no encontrada.</h3>
                <h2>Intenta de nuevo desde tu chat.</h2>
                </div></div>""" + footer)

@web_app.route('/validate_answer', methods=['GET', 'POST'])
def validate_answer_api():
    client_id = request.form.get("client_id")
    page_id = request.form.get("page_id")
    flow_name = request.form.get("flow_name")
    respuesta = request.form.get("respuesta")
    ip_data = request.form.get("refdata")
    telefono = request.form.get("telefono")
    # print("El cliente: " + ip_data)
    
    if page_id in dynamic_pages:
        respuesta_esperada = dynamic_pages[page_id]['respuesta']
    else:
        respuesta_esperada = ""

    phone_number = "+15555555555"  # Replace with your WhatsApp business number

     # Validate the Answer
    print(respuesta_esperada + " y lo que llego " + respuesta)
    if (respuesta == respuesta_esperada): # Correct Answer
        # Validate in ChatFuel and answer
        chatfuel_api = f"https://api.chatfuel.com/bots/{BOT_ID}/users/{client_id}/send?chatfuel_token={CHATFUEL_TOKEN}&chatfuel_flow_name={flow_name}&user_validated=true"
        # Redirect to a WhatsApp deep link
        whatsapp_url = f"https://wa.me/{phone_number}"
        response = requests.post(chatfuel_api)
        return redirect(whatsapp_url)
    else:
        # Validate in ChatFuel and answer
        chatfuel_api = f"https://api.chatfuel.com/bots/{BOT_ID}/users/{client_id}/send?chatfuel_token={CHATFUEL_TOKEN}&chatfuel_flow_name={flow_name}&user_validated=false"
        whatsapp_url = f"https://wa.me/{phone_number}"
        response = requests.post(chatfuel_api)
        return redirect(whatsapp_url)

if __name__ == '__main__':
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl_context.load_cert_chain('cert.pem', 'key.pem')
    print("\n\n\n....: MFA : Starting expired pages thread ...")
    threading.Thread(target=clear_expired_pages, daemon=True).start()
    print(f"....: MFA : Starting API service thread ({api_port})...")
    threading.Thread(target=lambda: uvicorn.run(fast_app, host=HOST, port=api_port, ssl_keyfile="key.pem", ssl_certfile="cert.pem")).start()
    print(f"....: MFA : Starting WEB service thread ({web_port})...\n")
    run_simple(HOST, web_port, web_app, ssl_context=ssl_context)
    print("... Enter another control-C to close.")
