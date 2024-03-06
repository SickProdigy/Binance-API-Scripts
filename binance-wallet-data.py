import urllib.parse
import hashlib
import hmac
import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()

# binance.us api url

api_url = "https://api.binance.us"

# get binanceus signature
def get_binanceus_signature(data, secret):
    postdata = urllib.parse.urlencode(data)
    message = postdata.encode()
    byte_key = bytes(secret, 'UTF-8')
    mac = hmac.new(byte_key, message, hashlib.sha256).hexdigest()
    return mac

# Attaches auth headers and returns results of a POST request
def binanceus_request_key(uri_path, data, api_key, api_sec):
    headers = {}
    headers['X-MBX-APIKEY'] = api_key
    signature = get_binanceus_signature(data, api_sec) 
    params={
        **data,
        "signature": signature,
        }
    req = requests.get((api_url + uri_path), params=params, headers=headers)
    return req.text

def binanceus_request(uri_path):
    req = requests.get((api_url + uri_path))
    return req.text

# create a file named '.env' with the below keys like so: BINANCE_API_KEY="mysuperlongbinancekey"
api_key = os.environ.get("BINANCE_API_KEY")
secret_key = os.environ.get("BINANCE_SECRET_KEY")

# uri_path = "/api/v3/ticker/price" # URI NO KEY initial api link doesn't require auth, 2 columns simple data
# uri_path = "/api/v3/openOrders"  # get all open orders
uri_path = "/sapi/v1/capital/config/getall" # asset fees and wallet status get all

data_time_stamp = {
    "timestamp": int(round(time.time() * 1000))
}

# here we pull the data
# result = binanceus_request(uri_path)      # URI NO KEY
result = binanceus_request_key(uri_path, data_time_stamp, api_key, secret_key)

print(result)