from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Binding:
    path: Optional[str]
    object: Optional[Any]
    factory: Optional[Any]
    instance: Optional[Any]
    kwargs: Optional[Dict]
    singleton: bool
    aliases: List


class Ioc(ABC):
    @property
    @staticmethod
    def bindings(self) -> Dict[str, Binding]:
        pass

    @property
    @staticmethod
    def aliases(self) -> Dict[str, str]:
        pass


    # @abstractmethod
    # def make(self, name: str) -> Any: pass

    # @abstractmethod
    # def merge_map(self, mapping: Dict) -> None: pass
