##############################################################
# 2FA Second Factor Authenticator for Whatsapp/Chat Bots     #
# Marvin Nahmias, 2024.                                      #
##############################################################

import ssl, string, time, threading, requests, random, uvicorn, re, sqlite3
from datetime import datetime, timedelta
from werkzeug.serving import run_simple
from flask import Flask, render_template, request, redirect
from fastapi import FastAPI, HTTPException, Request

# Server (Replace with the server you are hosting with if you like)
HOST = "0.0.0.0" # localhost
URL_SUFFIX = "https://" + HOST
CHATFUEL_TOKEN = "YOUR CHATFUEL TOKEN"
BOT_ID = "YOUR CHATFUEL BOT ID"
# Seconds to delete dynamic generated pages (ex: 300 = 5 min)
expiration = 60
phone_number = "+520000000000"  # Replace with your WhatsApp business number
whatsapp_url = f"https://wa.me/{phone_number}"
# Dictionary to store dynamic web pages and their expiration times in memory
dynamic_pages = {}
# Mutex for thread safety
mutex = threading.Lock()

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
                <title>2FA</title>
                <!-- Bootstrap CSS -->
                <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
                <!-- Bootstrap JS -->
                <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.bundle.min.js"></script>
            </head>
            <body>
     """

footer = f"""
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

new_ip_data = """
<script>
    // Function to fetch IP address
    async function getIPAddress() {
        const response = await fetch('https://api.ipify.org?format=json');
        const data = await response.json();
        return data.ip;
    }

    // Function to fetch location data based on IP
    async function getLocation(ip) {
        const response = await fetch('https://ipapi.co/' + ip + '/json/');
        const data = await response.json();
        return data;
    }

    // Function to get browser and device information
    function getBrowserAndDeviceInfo() {
        const browserInfo = {
            userAgent: navigator.userAgent,
            language: navigator.language,
            platform: navigator.platform,
            cookieEnabled: navigator.cookieEnabled,
            screenWidth: window.screen.width,
            screenHeight: window.screen.height,
            screenWidthAvailable: window.screen.availWidth,
            screenHeightAvailable: window.screen.availHeight
        };
        return browserInfo;
    }

    // Function to update the hidden field with IP, location, browser, and device data
    async function updateHiddenField() {
        try {
            const ip = await getIPAddress();
            const locationData = await getLocation(ip);
            const browserDeviceInfo = getBrowserAndDeviceInfo();

            // Constructing a JSON string with IP, location, browser, and device data
            const blobData = JSON.stringify({
                ip: ip,
                city: locationData.city,
                country: locationData.country_name,
                latitude: locationData.latitude,
                longitude: locationData.longitude,
                browserInfo: browserDeviceInfo
            });

            // Update the hidden field
            document.getElementById('refdata').value = blobData;

            // Return the blob data
            return blobData;
        } catch (error) {
            console.error('Error fetching IP, location, browser, and device info:', error);
            return null; // Return null if an error occurs
        }
    }
    // Call the update function when the page loads
    window.onload = async function() {
        const updatedData = await updateHiddenField();
        // You can use 'updatedData' here if needed
    };
</script>
"""

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
	        <h3>Please answer in <span id="countdowntimer" class="badge badge-secondary">{expiration} sec</span></h3>
            <div class="alert alert-primary" role="alert"><bold>{pregunta}</bold></div>
            <form method="post" action="/validate_answer">
                <input type="hidden" id="client_id" name="client_id" value="{client_id}">
                <input type="hidden" id="telefono" name="telefono" value="{telefono}">
                <input type="hidden" id="page_id" name="page_id" value="{page_id}">
                <input type="hidden" id="flow_name" name="flow_name" value="{flow_name}">
                <input type="hidden" id="refdata" name="refdata" value="">
                """
    dynamic_questions = preguntas(pregunta, options) 
    
    dynamic_end = """
                </br><center><button type="submit" class="btn btn-success">Validate</button></center>
            </form>"""
    
    dynamic_page += header + dynamic_questions + dynamic_end + new_ip_data + footer
    
    return dynamic_page

def clear_expired_pages():
    while True:
        current_time = time.time()
        try:
            with mutex:
                expired_pages = [page_id for page_id in dynamic_pages if dynamic_pages[page_id]['expiration_time'] < current_time]
                for page_id in expired_pages:
                    del dynamic_pages[page_id]
                    print(f"--- Deleted: {page_id}")
        except:
            print("--- Dynamic Array resized.")

        time.sleep(expiration + 1)  # Check expiration + 1 seg

def sum_month_day(date):
    # Extract month and day from the date
    month, day = map(int, date.split('-')[1:])
    # Sum the entire numbers of month and day
    return month + day

def generate_birth_dates_none(correct_date):
    # Convert the correct date string to a datetime object
    correct_date_obj = datetime.strptime(correct_date, '%Y-%m-%d')
    
    # Generate four unique random dates
    options = set()
    while len(options) < 4:
        days_difference = random.randint(-60, 60)
        random_date = correct_date_obj + timedelta(days=days_difference)
        if random_date != correct_date_obj:  # Exclude the correct date
            options.add(random_date.strftime('%Y-%m-%d'))
    
    # Convert set to list
    options_list = list(options)
    
    # Add the correct date to the options
    options_list.append(correct_date)
    
    # Shuffle options
    random.shuffle(options_list)
    
    # Check if "None of the options" should be included
    none_option = "None of the options."
    if random.random() < 0.50:  # Probability of 50% for "None of the options" to be included
        # Randomly select an index to replace with "None of the options"
        replace_index = random.randint(0, min(len(options_list)-1, 4))
        if options_list[replace_index] == correct_date:
            options_list[replace_index] = none_option
            flag = True
        else:
            options_list[replace_index] = none_option
            flag = False
    else:
        flag = False
    
    return (options_list, flag)

def generate_sums_none(correct_date):
    # Calculate the sum of the correct date's digits
    correct_sum = sum(int(digit) for digit in correct_date.split('-')[1:])
    
    # Generate four unique random sums
    options = set()
    while len(options) < 4:
        random_sum = random.randint(2, 12)  # Minimum sum is 2 (for January 1st)
        if random_sum != correct_sum:  # Exclude the correct sum
            options.add(random_sum)
    
    # Convert set to list
    options_list = list(options)
    
    # Add the correct sum to the options
    options_list.append(correct_sum)
    
    # Shuffle options
    random.shuffle(options_list)
    
    # Calculate the sum of the month and day
    month = int(correct_date.split('-')[1])
    day = int(correct_date.split('-')[2])
    correct_sum_md = month + day
    
    # Add the sum of month and day to the options
    options_list.append(correct_sum_md)
    
    # Check if "None of the options" should be included
    none_option = "None of the options."
    if random.random() < 0.50:  # Probability of 50% for "None of the options" to be included
        # Randomly select an index to replace with "None of the options"
        replace_index = random.randint(0, min(len(options_list)-1, 4))
        if options_list[replace_index] == correct_sum:
            options_list[replace_index] = none_option
            flag = True
        else:
            options_list[replace_index] = none_option
            flag = False
    else:
        flag = False
    
    # Ensure exactly 5 options are returned
    if len(options_list) > 5:
        options_list = options_list[:5]
    
    return (options_list, flag)

def preguntas(question_text, options):
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
fast_app = FastAPI(
    title="MFA - NoNoAPP",
    description="2FA Dynamic Page Generator and Validator.",
    contact={
        "name": "Marvin NoNo.App",
        "url": "http://www.nonoapp.com/",
        "email": "marvin@nonoapp.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)
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
 
    possible_dates, flag_d = generate_birth_dates_none(fecha_cumple)
    possible_sums, flag_s = generate_sums_none(fecha_cumple)
    pregunta = ""
    respuestas = []

    if sel_preguntas == 1:
        pregunta = "¿What is your DOB?"
        respuestas = possible_dates
        if (flag_d == False):
            la_respuesta = fecha_cumple
        if (flag_d == True):
            la_respuesta = "None of the options."
    elif sel_preguntas == 2:
        pregunta = "¿What is the sum of your Month + Day of your DOB (M+D)?"
        respuestas = possible_sums
        if (flag_s == False):
            la_respuesta = str(sum_month_day(fecha_cumple))
        if (flag_s == True):
            la_respuesta = "None of the options."

    dynamic_page = generate_dynamic_page(client_id, page_id, flow_name, pregunta, respuestas, telefono)
    
    if dynamic_page:
        # Set expiration time for expiration time from now
        expiration_time = time.time() + expiration
        with mutex:
            dynamic_pages[page_id] = {'content': dynamic_page, 'expiration_time': expiration_time, 'respuesta': la_respuesta}
        return {"dynamic_url": f"{URL_SUFFIX}/{page_id}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate dynamic page.")

@web_app.route('/')
def index():
    return render_template('index.html')

@web_app.route('/<page_id>')
def dynamic_page(page_id):
    with mutex:
        if page_id in dynamic_pages:
            return dynamic_pages[page_id]['content']
        else:
            return (header + f"""
                    <div class="container mt-5">
                    <center>
	                    <img class="img-fluid" width="300" src="https://cdn-icons-png.flaticon.com/512/7380/7380525.png">
     	    	    </br></br>
                    </center>
                    <div class="row justify-content-md-center">
                    <div class="col-12 col-md-11 col-lg-9 col-xl-7 col-xxl-6 text-center text-black"></br>
                    <h5 class="display-4 fw-bold mb-3">Dynamic Page not found!</h5>
                    <h6>Try again from your whatsapp.</h6>
                    </div></div><center>
                    <a href="{whatsapp_url}" class="btn btn-success" role="button">Back to chat</a>
                    </center>
                    """ + footer)

@web_app.route('/validate_answer', methods=['GET', 'POST'])
def validate_answer_api():
    client_id = request.form.get("client_id")
    page_id = request.form.get("page_id")
    flow_name = request.form.get("flow_name")
    respuesta = request.form.get("respuesta")
    ip_data = request.form.get("refdata")
    telefono = request.form.get("telefono")
    
    if page_id in dynamic_pages:
        with mutex:
            respuesta_esperada = dynamic_pages[page_id]['respuesta']
    else:
        respuesta_esperada = ""

     # Validate the Answer
    if (respuesta == respuesta_esperada): # Correct Answer
        # Enter in DB
        insert_log(ip_data, telefono)
        # print("....: Logged: " + ip_data)
        # Validate in ChatFuel and answer
        chatfuel_api = f"https://api.chatfuel.com/bots/{BOT_ID}/users/{client_id}/send?chatfuel_token={CHATFUEL_TOKEN}&chatfuel_flow_name={flow_name}&user_validated=true"
        # Redirect to a WhatsApp deep link after posting to chatfuel
        response = requests.post(chatfuel_api)
        return redirect(whatsapp_url)
    else:
        # Validate in ChatFuel and answer
        chatfuel_api = f"https://api.chatfuel.com/bots/{BOT_ID}/users/{client_id}/send?chatfuel_token={CHATFUEL_TOKEN}&chatfuel_flow_name={flow_name}&user_validated=false"
         # Redirect to a WhatsApp deep link after posting to chatfuel
        response = requests.post(chatfuel_api)
        return redirect(whatsapp_url)

if __name__ == '__main__':
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    ssl_context.load_cert_chain('certificate.crt', 'private.key')
    print("\n\n\n....: MFA : Starting expired pages thread ...")
    threading.Thread(target=clear_expired_pages, daemon=True).start()
    print(f"....: MFA : Starting API service thread ({api_port})...")
    threading.Thread(target=lambda: uvicorn.run(fast_app, host=HOST, port=api_port, ssl_keyfile="private.key", ssl_certfile="certificate.crt")).start()
    print(f"....: MFA : Starting WEB service thread ({web_port})...\n")
    run_simple(HOST, web_port, web_app, ssl_context=ssl_context)
    print("... Enter another control-C to close.")
