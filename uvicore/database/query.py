from __future__ import annotations

import operator as operators
from copy import copy
from typing import Any, Dict, Generic, List, Tuple, TypeVar, Union
import sqlalchemy as sa


import uvicore
from uvicore.support.dumper import dd, dump
from uvicore.database.builder import Query, Builder


E = TypeVar('E')

class QueryBuilder(Builder):
    """Database Query Builder"""

    def __init__(self, connection: str):
        self.connection = connection
        super().__init__()

    def table(self, table: str) -> QueryBuilder[E]:
        self.query.table = uvicore.db.table(table, self.connection)
        return self

    def select(self, *args) -> QueryBuilder[E]:
        for column in args:
            self.query.selects.append(column)
        return self

    def join(self, table: str, left_where: str, right_where: str):
        self.query.joins.append((table, left_where, right_where, 'inner'))
        return self

    def outer_join(self, table: str, left_where: str, right_where: str):
        self.query.joins.append((table, left_where, right_where, 'outer'))
        return self

    async def find(self, pk_value: Any) -> E:
        dump('find here')

    async def get(self) -> List[E]:
        # Build query
        query, saquery = self._build_query('select', copy(self.query))

        # Execute query
        results = await uvicore.db.fetchall(saquery, connection=self.connection)

        return results
