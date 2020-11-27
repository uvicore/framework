from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

class Relation(ABC):

    @abstractmethod
    def fill(self, field: Field) -> Relation:
        pass

    @abstractmethod
    def is_one(self) -> bool:
        pass

    @abstractmethod
    def is_many(self) -> bool:
        pass

    @abstractmethod
    def is_type(self, *args) -> bool:
        pass

    @abstractmethod
    def contains_many(self, relations, skip: List = []) -> bool:
        pass


# At bottom due to circular issues between these two contracts
from .field import Field  # isort:skip
