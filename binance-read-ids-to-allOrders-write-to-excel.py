import urllib.parse
import hashlib
import hmac
import base64
import requests
import time
import pandas as pd
import io
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

api_url = "https://api.binance.us" # don't use wrong link scalar values error

# create a file named '.env' with the below keys like so: BINANCE_API_KEY="mysuperlongbinancekey"
api_key = os.environ.get("BINANCE_API_KEY")
secret_key = os.environ.get("BINANCE_SECRET_KEY")

def get_binanceus_signature(data, secret):
    postdata = urllib.parse.urlencode(data)
    message = postdata.encode()
    byte_key = bytes(secret, 'UTF-8')
    mac = hmac.new(byte_key, message, hashlib.sha256).hexdigest()
    return mac

# Attach auth headers and return results from POST request
def binanceus_request_key(uri_path, data, api_key, api_sec):
    headers = {}
    headers['X-MBX-APIKEY'] = api_key
    signature = get_binanceus_signature(data, api_sec)
    params={
        **data,
        "signature": signature,
    }
    req = requests.get((api_url + uri_path), headers=headers, params=params)
    return req.text

uri_path = "/api/v3/allOrders"

out_path = "E:\\prodigy\\Scripts\\api-testing\\binance\\"  # windows needs double \\ escape the escape

df_nest_symbols = pd.read_excel(out_path + "binance.xlsx", sheet_name="BinanceCoinListManual", usecols="N", header=0) # using header none is the way, 0 = first row header

# print(df_nest_symbols) # prints pandas.DataFrame read from excel sheet

# time to loop that data in multiple calls. while also appending the data from the calls to another pandas.Dataframe
appended_data = []
for row in df_nest_symbols.itertuples():
    data_symbol = {
        "timestamp": int(time.time() * 1000),
        "symbol": str.upper(row.binanceid)
    }
    print(data_symbol)
    print("reading JSON data...")
    result=binanceus_request_key(uri_path, data_symbol, api_key, secret_key)
    print(result)
    print("reading JSON data into DataFrame...")
    df_nest = pd.read_json(io.StringIO(result))
    print("DataFrame created succesfully")
    
    print("DataFrame Shape:", df_nest.shape) # show dataframe is expanding
    
    appended_data.append(df_nest)

appended_data = pd.concat(appended_data)

# now write all that data to excel sheet
try:
    with pd.ExcelWriter(out_path + 'binance.xlsx', mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
        appended_data.to_excel(writer, sheet_name="BinanceAllOrders", index=False)
    print("DataFrame written to Excel")
except Exception as e:
    print(f"Error: {e}")

