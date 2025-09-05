import os
import requests
import json
import time
import hashlib
import random
import uuid
from datetime import datetime
import ctypes

ctypes.windll.kernel32.SetConsoleTitleW("POPMART MONITOR")

WEBHOOK_URL = ""

def log(message: str) -> None:
    """Print message with current date and time to the second."""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{current_time}] {message}")

def send_discord_message(content) -> None:
    """
    Sends a message to the pre-defined Discord webhook.
    If the content is JSON (as a dict, list, or a JSON string), it sends it in a pretty format.
    """
    # Try to prettify the content if possible.
    prettified = None
    if isinstance(content, (dict, list)):
        prettified = json.dumps(content, indent=4)
    elif isinstance(content, str):
        try:
            data = json.loads(content)
            prettified = json.dumps(data, indent=4)
        except Exception:
            # Not valid JSON, just use the string as-is.
            prettified = content
    else:
        prettified = str(content)
    
    payload = {
        "content": prettified,
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers=headers)
    
    if response.status_code in [200, 204]:
        log("Discord message sent successfully!")
    else:
        log(f"Failed to send Discord message. Status code: {response.status_code}")
        log(f"Response: {response.text}")

def generate_signature(client_id):
    """
    Generate the X-Sign signature used by the API.
    It uses the formula: MD5(f"{timestamp},{client_id}") + ',' + timestamp
    """
    timestamp = int(time.time())
    to_hash = f"{timestamp},{client_id}"
    hash_val = hashlib.md5(to_hash.encode()).hexdigest()
    return f"{hash_val},{timestamp}"

def generate_s_data(spu_id, secret_key="W_ak^moHpMla"):
    """
    Generate the 's' and 't' parameters for the request.
    It creates a JSON string for the spuId and computes:
        MD5( f'{{"spuId":"{spu_id}"}}' + secret_key + timestamp )
    Returns the hash value (as s) and the timestamp (t).
    """
    timestamp = int(time.time())
    jsonData = f'{{"spuId":"{spu_id}"}}'
    to_hash = jsonData + secret_key
    hash_val = hashlib.md5(f"{to_hash}{timestamp}".encode()).hexdigest()
    return hash_val, timestamp

def load_proxies(file_name: str) -> list:
    """
    Load proxy strings from a file.
    Each line in the file represents one proxy.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def get_random_proxy(proxies: list) -> dict:
    """
    Select a random proxy from the list and return a dictionary formatted for requests.
    """
    proxy = random.choice(proxies)
    return {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }

# Define your credentials and product parameters:
client_id = "nw3b089qrgw9m7b7i"
spu_id = "675"
URL = 'https://prod-global-api.popmart.com/shop/v1/shop/productDetails'

def build_request_data():
    """
    Build the dynamic request parameters and headers.
    Note that some fields are time-sensitive and re-generated each call.
    """
    x_sign = generate_signature(client_id)
    s, t = generate_s_data(spu_id)
    #log(f"Generated X-Sign: {x_sign}")
    #log(f"Generated s: {s} t: {t}")
    
    params = {
        'spuId': spu_id,
        's': s,
        't': str(t),
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'tz': 'America/Chicago',
        'X-Project-ID': 'naus',
        'X-Device-OS-Type': 'web',
        'ClientKey': client_id,
        'X-Sign': x_sign,
        'Country': 'US',
        'X-Client-Country': 'US',
        'X-Client-Namespace': 'america',
        'Language': 'en',
        'Origin': 'https://www.popmart.com',
        'Referer': 'https://www.popmart.com/',
    }
    
    return params, headers

def check_stock(proxies_list: list) -> bool:
    """
    Make a single stock check request using a randomly chosen proxy.
    Returns True if a "happy" response is obtained, otherwise False.
    A happy response means we got a valid JSON response with either
    in-stock or out-of-stock information.
    """
    print('-+-+-+')
    params, headers = build_request_data()
    proxy_config = get_random_proxy(proxies_list)
    #log(f"Using proxy: {proxy_config}")
    
    try:
        response = requests.get(URL, headers=headers, params=params, proxies=proxy_config, timeout=10)
        print(response)
        #print(response.text)
    except Exception as e:
        log(f"Request failed with exception: {e}")
        return False

    if response.status_code != 200:
        log(f"Unexpected status code: {response.status_code}")
        return False

    try:
        content = response.json()
    except Exception as e:
        log(f"Failed to decode JSON: {e}")
        return False

    # Check stock status from the JSON response.
    try:
        sku0 = content['data']['skus'][0]['stock']
        sku1 = content['data']['skus'][1]['stock']

        if (sku0['onlineStock'] != 0 or sku0['onlineLockStock'] != 0 or 
            sku1['onlineStock'] != 0 or sku1['onlineLockStock'] != 0):
            log("Stock detected!")
            send_discord_message({
                "message": f"STOCK DETECTED: https://www.popmart.com/us/products/{spu_id}/THE-MONSTERS---Exciting-Macaron-Vinyl-Face-Blind-Box",
                "skus": content['data']['skus']
            })
        else:
            log("Out of stock (OOS).")
            #send_discord_message({"skus": content['data']['skus']})
        return True  # A happy response.
    except Exception as e:
        log(f"Error while checking stock: {e}")
        send_discord_message({"error": str(e)})
        return False

def monitor_stock():
    """
    Checks stock every 3 seconds. If a request fails (i.e. doesn't produce
    an in-stock or OOS happy response), it retries up to 5 times with new proxies.
    If all retries fail, the monitor shuts down.
    """
    proxies_list = load_proxies("proxies.txt")
    
    while True:
        log("Grabbing latest stock update ...")
        happy_flow = check_stock(proxies_list)
        
        if not happy_flow:
            log("Initial request failed or returned an invalid response; initiating retries...")
            retry_count = 0
            while retry_count < 10 and not happy_flow:
                retry_count += 1
                log(f"Retry attempt {retry_count} ...")
                happy_flow = check_stock(proxies_list)
                if happy_flow:
                    break
                time.sleep(1)  # Small delay between retries
            if not happy_flow:
                log("No happy response after 5 retries; shutting script down.")
                send_discord_message("**SCRIPT IS NOW DOWN AFTER 5 FAILED ATTEMPTS!**")
                return  # Exit the monitor

        # Wait 3 seconds before checking again.
        time.sleep(2)

if __name__ == '__main__':
    monitor_stock()
