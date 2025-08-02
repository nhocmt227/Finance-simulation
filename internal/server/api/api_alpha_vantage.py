from dotenv import load_dotenv
import requests
import os

from internal.server.api.pull_based_api_template import PullBasedAPI
from internal.server.utils.exception import ApiLimitError

# take environment variables from .env.
load_dotenv()

API_KEY_ALPHA_VANTAGE = os.getenv("ALPHA_VANTAGE_API_KEY")

GLOBAL_QUOTE_URL = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={apikey}"
LISTING_STATUS_URL = (
    "https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={apikey}"
)


class AlphaVantageAPI(PullBasedAPI):
    def __init__(self):
        self.api_key = API_KEY_ALPHA_VANTAGE

    def lookup(self, symbol: str) -> dict:
        """
        Fetch stock data from Alpha Vantage without caching
        """
        symbol = symbol.upper()
        url = GLOBAL_QUOTE_URL.format(symbol=symbol, apikey=self.api_key)

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            if self.is_limited(data):
                raise ApiLimitError("API limit exceeded")

            stock_data = data.get("Global Quote", {})
            if self.is_invalid(stock_data):
                return None

            price = float(stock_data.get("05. price", 0))

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

    def get_all_active_stocks(self):
        """
        Optional implementation for fetching all stocks.
        """
        url = LISTING_STATUS_URL.format(apikey=self.api_key)

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            decoded = response.content.decode("utf-8")
            return [line.split(",") for line in decoded.splitlines()]
        except Exception as e:
            print(f"Error fetching active stocks: {e}")
            return None

    def is_invalid(self, data):
        return not data or "05. price" not in data

    def is_limited(self, data):
        return (
            isinstance(data, dict)
            and "Information" in data
            and "rate limit" in data["Information"].lower()
        )
