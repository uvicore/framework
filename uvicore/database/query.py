from __future__ import annotations

import operator as operators
from copy import copy
from typing import Any, Dict, Generic, List, Tuple, TypeVar, Union

import sqlalchemy as sa
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.engine.result import RowProxy

import uvicore
from uvicore.database.builder import _QueryBuilder, Join
from uvicore.support.dumper import dd, dump
from uvicore.contracts import DbQueryBuilder as BuilderInterface

B = TypeVar("B")  # Builder Type (DbQueryBuilder or OrmQueryBuilder)
E = TypeVar("E")  # Entity Model

@uvicore.service()
class _DbQueryBuilder(Generic[B, E], _QueryBuilder[B, E], BuilderInterface[B, E]):
    """Database Query Builder"""

    def __init__(self, connection: str):
        self._conn = connection
        super().__init__()

    def table(self, table: Union[str, sa.Table]) -> B[B, E]:
        if type(table) == str:
            self.query.table = uvicore.db.table(table, self._connection())
        else:
            self.query.table = table
        return self

    def select(self, *args) -> B[B, E]:
        for column in args:
            self.query.selects.append(column)
        return self

    def join(self, table: Union[str, sa.Table], left_where: Union[str, sa.Column, BinaryExpression], right_where: Union[str, sa.Column] = None, alias: str = None, method: str = 'join') -> B[B, E]:
        # Get table and tablename
        conn = self._connection()
        if type(table) == str:
            if '.' in table: conn, table = tuple(table.split('.'))
            table = uvicore.db.table(table, conn)
        tablename = str(table.name)

        # Get left, right and onclause expressions
        left = None
        right = None
        if type(left_where) == BinaryExpression:
            onclause = left_where
        else:
            left = self._column(left_where)
            right = self._column(right_where)
            onclause = left.sacol == right.sacol

        # Set alias to tablename if not defined
        if not alias: alias = tablename

        # Add new Join() expression
        self.query.joins.append(Join(table, tablename, left, right, onclause, alias, method))
        return self

    def outer_join(self, table: Union[str, sa.Table], left_where: Union[str, sa.Column, BinaryExpression], right_where: Union[str, sa.Column] = None, alias: str = None) -> B[B, E]:
        self.join(table=table, left_where=left_where, right_where=right_where, method='outerjoin', alias=alias)
        return self

    def group_by(self, *args) -> B[B, E]:
        for group_by in args:
            self.query.group_by.append(group_by)
        return self

    async def find(self, pk_value: Any) -> RowProxy:
        # Where on Primary Key
        self.where(self._pk(), pk_value)

        # Build query
        query, saquery = self._build_query('select', copy(self.query))

        # Execute query
        results = await uvicore.db.fetchone(saquery, connection=self._connection())

        return results

    async def get(self) -> List[RowProxy]:
        # Build query
        query, saquery = self._build_query('select', copy(self.query))

        # Execute query
        results = await uvicore.db.fetchall(saquery, connection=self._connection())

        return results

# IoC Class Instance
#_DbQueryBuilderIoc: _DbQueryBuilder = uvicore.ioc.make('DbQueryBuilder', _DbQueryBuilder)

# Actual Usable Model Class Derived from IoC Inheritence
#class DbQueryBuilder(Generic[B, E], _DbQueryBuilderIoc[B, E], BuilderInterface[B, E]):
    #pass
