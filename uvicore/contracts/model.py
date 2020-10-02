#from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Generic, TypeVar, Union, List, Tuple, Any

from uvicore.orm.mapper import Mapper
from uvicore.orm.query import QueryBuilder

E = TypeVar("E")

class Model(Generic[E], ABC):

    @abstractmethod
    def query(entity) -> QueryBuilder[E]:
        """Query builder passthrough"""
        pass

    # @abstractmethod
    # def where(entity, column: Union[str, List[Tuple]], operator: str = None, value: Any = None) -> QueryBuilder[E]:
    #     """Query builder passthrough"""
    #     pass

    @abstractmethod
    async def insert(entity, models: Union[List[E], List[Dict]]) -> None:
        """Insert one or more entities as List of entities or List of Dictionaries

        This bulk insert does NOT allow inserting child relations at the
        same time as there is no way to get each parents PK out to
        reference with each child in BULK. If you want to insert parent
        and relations at the same time use the slower non-bulk
        insert_with_relations() instead.
        """
        pass

    @abstractmethod
    async def insert_with_relations(entity, models: List[Dict]) -> None:
        """Insert one or more entities as List of Dict that DO have relations included

        Because relations are included, this insert is NOT bulk and must
        loop each row, insert the parent, get the PK, then insert each
        children (or children first then parent depending on BelongsTo vs
        HasOne or HasMany)
        """
        pass

    @abstractmethod
    def mapper(self_or_entity, *args) -> Mapper:
        """Entity mapper for model->table or table->model conversions

        Can be accessed both from the [static] class or from an instance
        """
        pass

    @abstractmethod
    async def create(self, relation: str, values: Union[List[Dict], Dict]) -> None:
        """Create related records and link them to the parent model"""
        pass

    @abstractmethod
    async def save(self) -> None:
        """Save this model to the database"""
        pass

    @abstractmethod
    async def delete(self) -> None:
        """Delete this model from the database"""
        pass
