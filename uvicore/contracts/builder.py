from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Tuple, TypeVar, Union

import sqlalchemy as sa
from sqlalchemy.engine.result import RowProxy
from sqlalchemy.sql.expression import BinaryExpression

B = TypeVar("B")  # Builder Type (DbQueryBuilder or OrmQueryBuilder)
E = TypeVar("E")  # Entity Model


class QueryBuilder(Generic[B, E], ABC):
    @abstractmethod
    def where(self, column: Union[str, BinaryExpression, List[Union[Tuple, BinaryExpression]]], operator: str = None, value: Any = None) -> B[B, E]:
        pass

    @abstractmethod
    def or_where(self, wheres: List[Union[Tuple, BinaryExpression]]) -> B[B, E]:
        pass

    @abstractmethod
    def order_by(self, column: Union[str, List[Tuple], Any], order: str = 'ASC') -> B[B, E]:
        pass

    @abstractmethod
    def limit(self, limit: int) -> B[B, E]:
        pass

    @abstractmethod
    def offset(self, offset: int) -> B[B, E]:
        pass

    @abstractmethod
    def sql(self, method: str = 'select') -> str:
        pass


class DbQueryBuilder(QueryBuilder[B, E], ABC):
    @abstractmethod
    def table(self, table: Union[str, sa.Table]) -> B[B, E]:
        pass

    @abstractmethod
    def select(self, *args) -> B[B, E]:
        pass

    @abstractmethod
    def join(self, table: Union[str, sa.Table], left_where: Union[str, sa.Column, BinaryExpression], right_where: Union[str, sa.Column] = None, alias: str = None, method: str = 'join') -> B[B, E]:
        pass

    @abstractmethod
    def outer_join(self, table: Union[str, sa.Table], left_where: Union[str, sa.Column, BinaryExpression], right_where: Union[str, sa.Column] = None, alias: str = None) -> B[B, E]:
        pass

    @abstractmethod
    def group_by(self, *args) -> B[B, E]:
        pass

    @abstractmethod
    async def find(self, pk_value: Any) -> RowProxy:
        pass

    @abstractmethod
    async def get(self) -> List[RowProxy]:
        pass


class OrmQueryBuilder(QueryBuilder[B, E], ABC):
    @abstractmethod
    def include(self, *args) -> B[B, E]:
        pass

    @abstractmethod
    def filter(self, column: Union[str, BinaryExpression, List[Tuple]], operator: str = None, value: Any = None) -> B[B, E]:
        """Filter child relationship by this AND clause"""
        pass

    @abstractmethod
    def or_filter(self, filters: List[Union[Tuple, BinaryExpression]]) -> B[B, E]:
        """Filter child relationship by this OR clause"""
        pass

    @abstractmethod
    def key_by(self, field: str) -> B[B, E]:
        pass

    @abstractmethod
    async def find(self, pk_value: Any) -> E:
        pass

    @abstractmethod
    async def get(self) -> Union[List[E], Dict[str, E]]:
        pass

