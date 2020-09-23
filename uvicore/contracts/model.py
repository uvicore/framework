#from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict


class Model(ABC):

    @abstractmethod
    async def save(self):
        """Save this model to the database"""
        pass

    @abstractmethod
    async def delete(self):
        """Delete this model from the database"""
        pass

    @abstractmethod
    def to_table(self) -> Dict:
        """Convert an model entry into a dictionary matching the tables columns"""
        pass
