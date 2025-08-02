class StockAggregator:
    def __init__(self, apis: list):
        self.apis = apis

    def lookup(self, symbol: str) -> dict:
        for api in self.apis:
            try:
                result = api.lookup(symbol)
                if result:
                    return result
            except Exception:
                continue
        return {"error": True}
