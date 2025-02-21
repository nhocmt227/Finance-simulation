from dotenv import load_dotenv
import requests
import os
import urllib.request
import urllib.parse
import json
import csv

# Stock lookup
def lookup(symbol, api_key):
    symbol = symbol.upper()
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an error for HTTP issues
        data = response.json()

        # Check for API rate limit 
        if is_limited(data):
            return None
        
        stock_data = data.get("Global Quote", {})

        if is_invalid(data):
            return None
        
        symbol = data.get("01. symbol")
        price = float(data.get("05. price", 0))  # Convert safely to float

        return {"symbol": symbol, "price": price}
    except requests.exceptions.Timeout:
        print("Error: Request timed out.")
        return {"error": "Request timed out. Try again later."}
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request Error: {e}")
    except KeyError as e:
        print(f"Missing Key in Response: {e}")
    except ValueError as e:
        print(f"Value Conversion Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    return None

# The size can be very big
def get_all_active_stocks(api_key):
    # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
    try:
        CSV_URL = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}'
        stocks = []
        with requests.Session() as s:
            download = s.get(CSV_URL)
            decoded_content = download.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list = list(cr)
            for row in my_list:
                stocks.append(row)
            return stocks
    except (KeyError, ValueError, IndexError):
        print("Error in get_all_active_stocks function")
        return None

# Get n stocks
def get_all_active_stocks(api_key, amount):
    # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
    try:
        CSV_URL = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}'
        stocks = []
        with requests.Session() as s:
            download = s.get(CSV_URL)
            decoded_content = download.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list = list(cr)
            count = 0
            for row in my_list:
                if (count >= amount):
                    return stocks
                else:
                    stocks.append(row)
                    count += 1
    except (ValueError, IndexError, KeyError):
        print("Error in get_all_active_stocks function")
        return None

def is_invalid(data):
    if data is None or data == {}:
        return True
    else:
        return False
    
def is_limited(data):
    if isinstance(data, dict) and "Information" in data:
        message = data["Information"]
        if "rate limit" in message.lower():
            print(f"API rate limit exceeded: {message}")
            return True
    return False

def pretty_print(data):
    pretty_json = json.dumps(data, indent=4)
    print(pretty_json)

if __name__ == "__main__":
    # take environment variables from .env.
    load_dotenv()  
    # Retrieve the API key
    API_KEY = os.getenv("API_KEY")
    print(f'API_KEY: {API_KEY}')

    symbol = "TSLA"
    
    quote_data = get_quote(symbol, API_KEY)
    pretty_print(quote_data)
