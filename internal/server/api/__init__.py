from internal.server.api.pull_based_aggregator import StockAggregator
from internal.server.api.api_alpha_vantage import AlphaVantageAPI

# Instantiate the APIs
alpha_vantage_api = AlphaVantageAPI()
apis = [alpha_vantage_api]

# Create a singleton StockAggregator
stock_aggregator = StockAggregator(apis=apis)
