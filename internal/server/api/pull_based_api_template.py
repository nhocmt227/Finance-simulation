from abc import ABC, abstractmethod


class PullBasedAPI(ABC):
    @abstractmethod
    def lookup(self, symbol: str) -> dict:
        pass
