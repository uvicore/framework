from abc import ABC, abstractmethod
from typing import Dict


class Config(ABC):

    @abstractmethod
    def get(self, dotkey: str = None, config: Dict = None):
        pass

    @abstractmethod
    def set(self, dotkey: str, value: any, config: Dict = None):
        pass

    @abstractmethod
    def merge(self, dotkey: str, value: any):
        pass
