#from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Generic, TypeVar, Union, List, Tuple, Any

class Mapper(ABC):

    @abstractmethod
    def column(self) -> str:
        """Convert a model field name into a table column name"""

    @abstractmethod
    def field(self):
        """Convert a table column name into a model field name"""

    @abstractmethod
    def model(self, perform_mapping: bool = True):
        """Convert a dict or List[dict] into a model or List[Model]

        Only maps table->model fields if perform_mapping = True, else assume already model fields.
        Works on a single record as dict - entity.mapper(DictModel).model()
        Works on a list of dict - entity.mapper(ListOfDictModel).model()
        Passes through if already a Model or List[Model]
        If mixed List of Dict and Model, converts all to Models
        """

    @abstractmethod
    def table(self):
        """Convert an model instance into a dictionary matching the tables columns (column mapper enabled)

        Works on a single model - model.mapper().table() or entity.mapper(model).table()
        Or on a list of model instances - entity.mapper(ListOfModelInstances).tabel()
        Or on a list of model dictionaries - entity.mapper(ListOfModelDict).table()
        Does not convert or recurse into relations
        """
