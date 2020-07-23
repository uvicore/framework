from abc import ABC, abstractmethod
from typing import Dict, Any


class Config(ABC):

    @property
    @abstractmethod
    def items(self) -> Dict:
        """Dictinoary of all packages deep_merged configs"""
        pass

    @abstractmethod
    def get(self, dotkey: str = None, config: Dict = None) -> Any:
        pass

    @abstractmethod
    def set(self, dotkey: str, value: any, config: Dict = None) -> Any:
        pass

    @abstractmethod
    def merge(self, dotkey: str, value: Any) -> None:
        pass
