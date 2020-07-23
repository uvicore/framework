from abc import ABC, abstractmethod
from typing import Dict, Any


class Logger(ABC):

    @abstractmethod
    def debug(self, message):
        pass

    @abstractmethod
    def info(self, message):
        pass
