from uvicore.typing import Dict


class Config(Dict):
    pass









# OBSOLETE, now SuperDict!


from abc import ABC, abstractmethod
from typing import Dict, Any
class ConfigOBSOLETE(ABC):

    @property
    @abstractmethod
    def items(self) -> Dict[str, Dict]:
        """Dictinoary of all packages deep_merged configs"""
        pass

    @abstractmethod
    def get(self, dotkey: str = None, _recursive_config: Dict = None) -> Any:
        """Get a config item by dotkey notation"""
        pass

    @abstractmethod
    def set(self, dotkey: str, value: any, _recursive_config: Dict = None) -> Any:
        """Set a config item by dotkey notation"""
        pass

    @abstractmethod
    def merge(self, dotkey: str, value: Any) -> None:
        """Deep merge value into all configs by dotkey notation"""
        pass
