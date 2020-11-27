#from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Generic, TypeVar, Union, List, Tuple, Any

class Mapper(ABC):

    @abstractmethod
    def column(self) -> str:
        """Convert a model field name into a table column name"""
        pass
