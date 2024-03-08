import urllib.parse
import hashlib
import hmac
import base64
import requests
import time
import xlwings,pandas # for excel sheets. pandas reads it, xlwings writes it; not sure if xlwings is needed anymore but pandas requires a few modules to be installed -pip install pandas[excel]
import io
from dotenv import load_dotenv
import os

load_dotenv()

# binance.us api url

api_url = "https://api.binance.us"

# create a file named '.env' with the below keys like so: BINANCE_API_KEY="mysuperlongbinancekey"
api_key = os.environ.get("BINANCE_API_KEY")
secret_key = os.environ.get("BINANCE_SECRET_KEY")

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

# uri_path = "/api/v3/ticker/price" # URI NO KEY initial api link doesn't require auth, 2 columns simple data
# uri_path = "/api/v3/openOrders"  # get all open orders
# uri_path = "/sapi/v1/capital/config/getall" # asset fees and wallet status get all
# uri_path = "/sapi/v1/staking/asset"  # staking assets, doesn't show amount staking just rates... dumb
# uri_path = "/sapi/v1/staking/stakingBalance"  # staking balances, shows amount staking
# uri_path = "/api/v3/openOrders" # Use this endpoint to get all open trade orders for a token symbol.
uri_path = "/api/v3/allOrders" # Get all account orders: active, canceled, or filled.

data_time_stamp = {
    "timestamp": int(round(time.time() * 1000)),
    "symbol": "BTCUSDC" # used in '/api/v3/allOrders'; symbol is mandatory
}

# here we pull the data

# result = binanceus_request(uri_path)      # URI NO KEY
# result = binanceus_request_key(uri_path, data_time_stamp, api_key, secret_key)
result = binanceus_request_key(uri_path, data_time_stamp, api_key, secret_key)

# here we create a dataframe from the data)
print("Reading JSON data into DataFrame...")
df_nested = pandas.read_json(io.StringIO(result)) # this works, don't use wrong uri_path
# df_nested = pandas.DataFrame.from_dict(result, orient='columns') # dictionary example doesn't work with json data
print("DataFrame created successfully.")

# print (df_nested) # to prove it works (176 rows x 14 columns)

# Check the shape of the DataFrame
print("DataFrame shape:", df_nested.shape) # will show if it's a dataframe or not i reckon

# print(df_nested.dtypes)
# print(df_nested)

out_path = "E:\\prodigy\\Scripts\\api-testing\\binance\\"  # windows needs double \\ escape the escape

try:
    # wb = xlwings.Book('binance.xlsx').sheets('BinanceWallet') # Method 1; file name and sheet page
    # wb.range('a1').options(pandas.DataFrame, index=False).value = pandas.DataFrame(df_nested) # works using URI NO KEY dataset, have to have file open
    
    # df_nested.to_excel(out_path + 'binance.xlsx', sheet_name='BinanceWallet', index=False) # Method 2; creates new file with sheet name, will delete current document and replace be careful
    
    with pandas.ExcelWriter(out_path + 'binance.xlsx', mode="a", engine="openpyxl", if_sheet_exists="replace") as writer: # mode="a" means append
        df_nested.to_excel(writer, sheet_name="BinanceAllOrders") # has more options that actually work, still need to pip install openpyxl though
    print(df_nested)
    print(out_path + 'binance.xlsx')
    print("Excel Sheet written successfully")
    
except Exception as e:
    print(f"Error: {e}")

# Only returning one symbols pair. For Loop in binance-read-coins-to-depositHistory-write-to-excel.py