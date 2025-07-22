from dotenv import load_dotenv
import os
import requests
import json
import csv
from datetime import datetime, timedelta

from internal.server.utils.exception import ApiLimitError
from internal.server.model.sqlite_connection import get_db

# take environment variables from .env.
load_dotenv()  
# Retrieve the API key
API_TIME_TO_UPDATE = int(os.getenv("API_TIME_TO_UPDATE"))

# Stock lookup
def lookup(symbol, api_key):
    """
    Perform API request to get stock information
    Args: 
        symbol: a string of stock_symbol, can be lowercase or uppercase
        api_key
    Returns:
        a dictionary contains 2 keys about the stock: "symbol" and "price"
    """

    print(API_TIME_TO_UPDATE)
    symbol = symbol.upper()
    conn = get_db()

    stock_row = conn.execute(
        "SELECT * FROM stock_status WHERE stock_symbol = ?",
        (symbol,)
    ).fetchone()

    now = datetime.now()
    print(now)

    if stock_row is not None:
        stock_price_time = stock_row["time"]

        # Convert stock_price_time from string to datetime
        stock_price_time = datetime.strptime(stock_price_time, "%Y-%m-%d %H:%M:%S")

        # Convert API_TIME_TO_UPDATE from int (seconds) to timedelta
        update_threshold = timedelta(seconds=API_TIME_TO_UPDATE)

        if ((datetime.now() - stock_price_time) <= update_threshold):
            return {"symbol": stock_row["stock_symbol"], "price": stock_row["stock_price"]}

    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an error for HTTP issues
        data = response.json() # Convert JSON-formatted string to dictionary

        print("API request on " + symbol)

        # Check for API rate limit 
        if is_limited(data):
            raise ApiLimitError("API Limit exceed, max 25 requests per day")

        if "Global Quote" in data:
            stock_data = data["Global Quote"]
        else:
            stock_data = None   

        if is_invalid(stock_data):
            return None
        
        symbol = stock_data.get("01. symbol")
        price = float(stock_data.get("05. price", 0))  # Convert safely to float

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = conn.execute("SELECT 1 FROM stock_status WHERE stock_symbol = ?", (symbol,))
        row = cursor.fetchone()

        if row:
            # Update if it exists
            conn.execute("UPDATE stock_status SET stock_price = ?, time = ? WHERE stock_symbol = ?", (price, now, symbol))
        else:
            # Insert if it does not exist
            conn.execute("INSERT INTO stock_status (stock_symbol, stock_price, time) VALUES (?, ?, ?)", (symbol, price, now))

        conn.commit()

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

def is_invalid(stock_data):
    """
    Check if the provided stock_data dictionary is invalid.

    The function expects stock_data to be a dictionary containing stock 
    information with keys such as '01. symbol', '05. price', etc.

    Args:
        stock_data (dict): A dictionary containing stock information.
    """
    if stock_data is None or stock_data == {}:
        return True
    else:
        return False
    
def is_limited(API_response):
    """
    Check if the API response exceed the rate limit 

    The function expects API_response to be a raw API response containing
    the key "Information".

    Args:
        API_response (any): The response from the API, expected to be a dictionary.
    """
    if isinstance(API_response, dict) and "Information" in API_response:
        message = API_response["Information"]
        if "rate limit" in message.lower():
            print(f"API rate limit exceeded: {message}")
            return True
    return False

def pretty_print(data):
    """
    pretty_print json data
    Args:
        data (dictionary type): 
    """
    pretty_json = json.dumps(data, indent=4)
    print(pretty_json)
