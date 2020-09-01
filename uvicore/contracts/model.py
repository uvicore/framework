#from __future__ import annotations
from abc import ABC, abstractmethod, abstractclassmethod
from typing import Dict, List, Any, Union


class Model(ABC):

    @abstractclassmethod
    def all(entity):
        """Get all records"""
        pass

    @abstractclassmethod
    def get(entity):
        """Get records defined by query builder"""
        pass

    @abstractclassmethod
    def find(entity, id: Any):
        """Get records defined by query builder"""
        pass

    @abstractclassmethod
    def insert(entity, values: List):
        """Insert an array of models in bulk"""
        pass

    @abstractclassmethod
    def where(entity, column: str, value: Any):
        """Get records defined by query builder"""
        pass

    @abstractclassmethod
    def _to_model(entity, row):
        """Convert a row of table data into a model"""
        pass

    @abstractmethod
    def _to_table(self):
        """Convert an model entry into a dictionary matching the tables columns"""
        pass

    # @property
    # @abstractmethod
    # def events(self) -> Dict: pass

    # @property
    # @abstractmethod
    # def listeners(self) -> Dict[str, List]: pass

    # @property
    # @abstractmethod
    # def wildcards(self) -> List: pass

    # @abstractmethod
    # def register(self, events: Dict):
    #     pass

    # @abstractmethod
    # def listen(self, events: Union[str, List], listener: Any) -> None:
    #     pass

    # @abstractmethod
    # def dispatch(self, event: Any, payload = {}) -> None:
    #     pass

    # @abstractmethod
    # def get_listeners(self, event: str) -> List:
    #     pass
