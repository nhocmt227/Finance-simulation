from internal.server.utils.exception import ApiLimitError


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
        raise ApiLimitError
