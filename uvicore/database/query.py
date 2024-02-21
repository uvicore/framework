from __future__ import annotations

import operator as operators
from copy import copy
from typing import Any, Dict, Generic, List, Tuple, TypeVar, Union
from uvicore.support.hash import sha1

import sqlalchemy as sa
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.engine.result import Row as RowProxy

import uvicore
from uvicore.database.builder import QueryBuilder, Join
from uvicore.support.dumper import dd, dump
from uvicore.contracts import DbQueryBuilder as BuilderInterface

B = TypeVar("B")  # Builder Type (DbQueryBuilder or OrmQueryBuilder)
E = TypeVar("E")  # Entity Model

@uvicore.service()
class DbQueryBuilder(Generic[B, E], QueryBuilder[B, E], BuilderInterface[B, E]):
    """Database Query Builder"""

    def __init__(self, connection: str):
        self._conn = connection
        super().__init__()

    def table(self, table: Union[str, sa.Table]) -> B[B, E]:
        """Add table (select) statement to query"""
        if type(table) == str:
            self.query.table = uvicore.db.table(table, self._connection())
        else:
            self.query.table = table

        if self.query.table is None:
            raise Exception('Table {} not found.  Are you missing a prefix?  Use uvicore.db.tablename() for proper prefixing.'.format(table))
        return self

    def select(self, *args) -> B[B, E]:
        """Add select (columns) statment to query"""
        for column in args:
            self.query.selects.append(column)
        return self

    def join(self, table: Union[str, sa.Table], left_where: Union[str, sa.Column, BinaryExpression], right_where: Union[str, sa.Column] = None, alias: str = None, method: str = 'join') -> B[B, E]:
        """Add join (default to INNER) statement to query"""
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
        """Add LEFT OUTER join statement to query"""
        self.join(table=table, left_where=left_where, right_where=right_where, method='outerjoin', alias=alias)
        return self

    def group_by(self, *args) -> B[B, E]:
        """Add group by statement to query"""
        for group_by in args:
            self.query.group_by.append(group_by)
        return self

    async def find(self, pk_value: Union[int, str] = None, **kwargs) -> RowProxy:
        """Execute query by primary key or custom column and return first row found"""
        if pk_value:
            # Assume column is PK .find(1234)
            column = self._pk()
            value = pk_value
        elif kwargs:
            # Pass in the column to find .find(email='xyz')
            column = [x for x in kwargs.keys()][0]
            value = [x for x in kwargs.values()][0]

        # Add in where on PK
        self.where(column, value)

        # Get results based on query results
        results = await self.get()

        # Return one record or None
        if results: return results[0]
        return None

    async def get(self) -> List[RowProxy]:
        """Execute select query and return all rows found"""

        # Build select query
        # Use copy() insteadd of .copy() or nested tables tables get deepcopied and SA sees
        # them as multiple tables thworing a 1066, "Not unique table/alias: 'posts'"
        query, saquery = self._build_query('select', copy(self.query))  # do NOT use .copy()

        # Detect caching
        cache = self.query.cache
        if cache:
            prefix = 'uvicore.database/'
            if cache.get('key') is None:
                # No cache name specified, automatically build unique based on queries
                cache['key'] = prefix + query.hash(
                    hash_type='sha1',
                    package='uvicore.database',
                    connection=self._conn,
                )
            else:
                cache['key'] = prefix + cache.get('key')

        # Get cache store from query builder, if None, uses default store
        if cache and await uvicore.cache.store(cache.get('store')).has(cache.get('key')):
            # Cache found, use cached results
            #dump('DB FROM CACHE')
            results = await uvicore.cache.store(cache.get('store')).get(cache.get('key'))
        else:
            # Execute query
            #dump('DB FROM DB')
            results = await uvicore.db.fetchall(saquery, connection=self._connection())

            # Add to cache if desired
            if cache: await uvicore.cache.store(cache.get('store')).put(cache.get('key'), results, seconds=cache.get('seconds'))

        return results

    async def delete(self) -> None:
        """Execute delete query"""

        # Build SQLAlchemy delete query
        query, saquery = self._build_query('delete', copy(self.query))

        # Execute query
        await uvicore.db.execute(saquery, connection=self._connection())

    async def update(self, **kwargs) -> None:
        """Execute update query"""

        # Build SQLAlchemy delete query
        query, saquery = self._build_query('update', copy(self.query))

        # Add in values
        saquery = saquery.values(**kwargs)

        # Execute query
        await uvicore.db.execute(saquery, connection=self._connection())
