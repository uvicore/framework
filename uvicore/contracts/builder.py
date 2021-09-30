from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Tuple, TypeVar, Union, Dict

try:
    import sqlalchemy as sa
    from sqlalchemy.engine.result import RowProxy
    from sqlalchemy.sql.expression import BinaryExpression
except ImportError:  # pragma: nocover
    sa = None  # type: ignore
    RowProxy = None  # type: ignore
    BinaryExpression = None  # type: ignore

B = TypeVar("B")  # Builder Type (DbQueryBuilder or OrmQueryBuilder)
E = TypeVar("E")  # Entity Model


class QueryBuilder(Generic[B, E], ABC):
    @abstractmethod
    def where(self, column: Union[str, BinaryExpression, List[Union[Tuple, BinaryExpression]]], operator: str = None, value: Any = None) -> B[B, E]:
        """Add where statement to query"""

    @abstractmethod
    def or_where(self, wheres: List[Union[Tuple, BinaryExpression]]) -> B[B, E]:
        """Add or where statement to query"""

    @abstractmethod
    def order_by(self, column: Union[str, List[str], List[Tuple], Any], order: str = 'ASC') -> B[B, E]:
        """Order results by these columns ASC or DESC order"""

    @abstractmethod
    def limit(self, limit: int) -> B[B, E]:
        """Limit results"""

    @abstractmethod
    def offset(self, offset: int) -> B[B, E]:
        """Limit offset"""

    @abstractmethod
    def cache(self, name: str = None) -> B[B, E]:
        """Cache results, None seconds uses cache backend default, 0=forever"""

    @abstractmethod
    def sql(self, method: str = 'select') -> str:
        """Get all SQL queries involved in this query builder"""


class DbQueryBuilder(QueryBuilder[B, E], ABC):
    @abstractmethod
    def table(self, table: Union[str, sa.Table]) -> B[B, E]:
        """Add table (select) statement to query"""

    @abstractmethod
    def select(self, *args) -> B[B, E]:
        """Add select (columns) statment to query"""

    @abstractmethod
    def join(self, table: Union[str, sa.Table], left_where: Union[str, sa.Column, BinaryExpression], right_where: Union[str, sa.Column] = None, alias: str = None, method: str = 'join') -> B[B, E]:
        """Add join (default to INNER) statement to query"""

    @abstractmethod
    def outer_join(self, table: Union[str, sa.Table], left_where: Union[str, sa.Column, BinaryExpression], right_where: Union[str, sa.Column] = None, alias: str = None) -> B[B, E]:
        """Add LEFT OUTER join statement to query"""

    @abstractmethod
    def group_by(self, *args) -> B[B, E]:
        """Add group by statement to query"""

    @abstractmethod
    async def find(self, pk_value: Any) -> RowProxy:
        """Execute query by primary key or custom column and return first row found"""

    @abstractmethod
    async def get(self) -> List[RowProxy]:
        """Execute select query and return all rows found"""

    @abstractmethod
    async def delete(self) -> None:
        """Execute delete query"""

class OrmQueryBuilder(QueryBuilder[B, E], ABC):
    @abstractmethod
    def include(self, *args) -> B[B, E]:
        """Include child relation models"""
        pass

    @abstractmethod
    def filter(self, column: Union[str, BinaryExpression, List[Union[Tuple, BinaryExpression]]], operator: str = None, value: Any = None) -> B[B, E]:
        """Filter child relationship by this AND clause"""
        pass

    @abstractmethod
    def or_filter(self, filters: List[Union[Tuple, BinaryExpression]]) -> B[B, E]:
        """Filter child relationship by this OR clause"""
        pass

    @abstractmethod
    def sort(self, column: Union[str, List[str], List[Tuple], Any], order: str = 'ASC') -> B[B, E]:
        """Sort Many relations only"""
        pass

    @abstractmethod
    def key_by(self, field: str) -> B[B, E]:
        """Key results as a Dictionary by this column"""
        pass

    @abstractmethod
    async def find(self, pk_value: Union[int, str] = None, **kwargs) -> Union[E, None]:
        """Execute query by primary key or custom column and return first row found"""
        pass

    @abstractmethod
    async def get(self) -> Union[List[E], Dict[str, E]]:
        """Execute a select query and return all rows found"""
        pass

    @abstractmethod
    async def delete(self) -> None:
        """Execute delete query"""
