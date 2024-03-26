import requests
import threading
import time
import socket

# Configuration
API_URL = "https://localhost/generate_dynamic_page"  
CLIENT_ID = "your_client_id"
PREGUNTA = "your_question"
NUM_REQUESTS = 1000  # Number of requests to send
NUM_THREADS = 100  # Number of threads to use
DNS_TIMEOUT = 2  # DNS resolution timeout in seconds
RETRY_DELAY = 1  # Delay between retry attempts in seconds
MAX_RETRIES = 3  # Maximum number of retry attempts

# Global variables
successful_requests = 0
error_count = 0

# Function to send GET request to API
def send_request():
    global successful_requests, error_count
    params = {
        "client_id": CLIENT_ID,
        "pregunta": PREGUNTA
    }
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.get(API_URL, params=params, timeout=(DNS_TIMEOUT, None), verify=False)
            if response.status_code == 200:
                successful_requests += 1
                return response.text
            else:
                print(f"Error: Unexpected status code {response.status_code}")
                error_count += 1
                return None
        except requests.exceptions.Timeout:
            print(f"Failed to resolve DNS within {DNS_TIMEOUT} seconds")
            error_count += 1
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error occurred: {e}")
            retries += 1
            print(f"Retrying... ({retries}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)
    print("Max retries exceeded.")
    error_count += 1
    return None

# Function to check if DNS resolution exists in hosts file
def check_dns_resolution():
    try:
        socket.gethostbyname("mfa.makersmexico.org")  # Replace "mfa.makersmexico.org" with your domain
        return True
    except socket.gaierror:
        return False

# Function to add DNS resolution to hosts file
def add_dns_resolution():
    with open("/etc/hosts", "a") as hosts_file:
        hosts_file.write("103.101.203.18 mfa.makersmexico.org\n")  # Replace "mfa.makersmexico.org" with your domain

# Function to perform load testing in a thread
def load_test_thread():
    for _ in range(NUM_REQUESTS // NUM_THREADS):
        response = send_request()
        if response:
            # Print response content
            print(f"Response content: {response}")

# Main function for load testing
def load_test():
    global successful_requests, error_count

    # Check if DNS resolution exists in hosts file, if not, add it
    if not check_dns_resolution():
        add_dns_resolution()

    start_time = time.time()
    threads = []
    for _ in range(NUM_THREADS):
        thread = threading.Thread(target=load_test_thread)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    end_time = time.time()

    total_time = end_time - start_time
    total_requests = successful_requests + error_count
    transactions_per_second = successful_requests / total_time

    print(f"Total time taken: {total_time} seconds")
    print(f"Total successful requests: {successful_requests}")
    print(f"Total errors: {error_count}")
    print(f"Total requests: {total_requests}")
    print(f"Transactions per second (TPS): {transactions_per_second}")

if __name__ == "__main__":
    load_test()

# 1000 tries with 100 threads. Running on Docker, no certificate checking.
# Total time taken: 6.910074949264526 seconds
# Total successful requests: 1000
# Total errors: 0
# Total requests: 1000
# Transactions per second (TPS): 144.7162306258972
