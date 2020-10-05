from __future__ import annotations

import operator as operators
from copy import copy
from typing import Any, Dict, Generic, List, Tuple, TypeVar, Union

import sqlalchemy as sa
from pydantic.utils import Representation

import uvicore
from uvicore.support.dumper import dd, dump

E = TypeVar('E')

class Query(Representation):
    __slots__ = (
        'includes',
        'selects',
        'wheres',
        'or_wheres',
        'filters',
        'or_filters',
        'order_by',
        'keyed_by',
        'relations',
        'joins',
        'table',
        #'extra',
    )

    def __init__(self):
        self.includes: List = []
        self.selects: List = []
        self.wheres: List[Tuple] = []
        self.or_wheres: List[Tuple] = []
        self.filters: List[Tuple] = []
        self.or_filters: List[Tuple] = []
        self.order_by: List[Tuple] = []
        self.keyed_by: str = None
        self.relations: Dict[str, Relation] = {}
        self.joins: List[Tuple] = []
        self.table: sa.Table
        #self.exra: Dict[str, Dict]


class Builder(Generic[E]):

    def __init__(self):
        self.query = Query()

    def where(self, column: Union[str, List[Tuple]], operator: str = None, value: Any = None) -> QueryBuilder[E]:
        if type(column) == str:
            # A single where as a string
            # .where('column', 'value')
            # .where('column, '=', 'value')
            if not value:
                value = operator
                operator = '='
            self.query.wheres.append((column, operator.lower(), value))
        else:
            # Multiple wheres in one as a List[Tuple]
            # .where([('column', 'value'), ('column', '=', 'value')])
            for where in column:
                # Recursivelly add Tuple wheres
                if len(where) == 2:
                    self.where(where[0], '=', where[1])
                else:
                    self.where(where[0], where[1], where[2])
        return self

    def or_where(self, wheres: List[Tuple]) -> QueryBuilder[E]:
        # Or where must be a list of tuple as it required at least 2 statements
        # .or_where([('column', 'value'), ('column', '=', 'value')])
        or_where: List[Tuple] = []
        for where in wheres:
            if len(where) == 2:
                or_where.append((where[0], '=', where[1]))
            else:
                or_where.append((where[0], where[1].lower(), where[2]))
        self.query.or_wheres.extend(or_where)
        return self

    def order_by(self, column: Union[str, List[Tuple]], order: str = 'ASC') -> QueryBuilder[E]:
        if type(column) == str:
            self.query.order_by.append((column, order.upper()))
        else:
            # Multiple order as a List[Tuple] (column, order)
            for order_by in column:
                if type(order_by) == tuple:
                    if len(order_by) == 1:
                        column = order_by[0]
                        order = 'ASC'
                    elif len(order_by) == 2:
                        column, order = order_by
                else:
                    column = order_by
                    order = 'ASC'
                self.order_by(column, order)
        return self

    def sql(self, method: str = 'select'):
        query, saquery = self._build_query('select', copy(self.query))
        return str(saquery)

    def _build_query(self, method: str, query: Query):
        # Convert our Query into SQLAlchemy query
        #saquery: sa.sql.select = None

        # where
        #   select
        #   update (not in insert)
        #   delete

        # insert will never come into this get() or build function

        if method == 'select':

            #saquery = sa.select([query.table])
            saquery = self._build_select(query)

            join_stmt = self._build_joins(query)
            if join_stmt is not None: saquery = saquery.select_from(join_stmt)

            # Order By
            if query.order_by:
                saquery = self._build_order_by(query, saquery)


        # Where And
        if query.wheres:
            where_ands = self._build_where(query, query.wheres)
            saquery = saquery.where(sa.and_(*where_ands))

        # Where Or
        if query.or_wheres:
            where_ors = self._build_where(query, query.or_wheres)
            saquery = saquery.where(sa.or_(*where_ors))

        return query, saquery

    def _build_order_by(self, query: Query, saquery):
        for order_by in query.order_by:
            column, order = order_by

            # Get actual table and column based on conn.table.column dot notation
            column, table = self._column_parts(column, query)

            if order == 'DESC':
                saquery = saquery.order_by(sa.desc(getattr(table.c, column)))
            else:
                saquery = saquery.order_by(getattr(table.c, column))
        return saquery


    def _column_parts(self, dotcol: str, query: Query):
        column = None
        table = None
        if '.' in dotcol:
            parts = dotcol.split('.')
            conn = None
            if len(parts) == 2:
                tablename, column = tuple(parts)
            if len(parts) == 3:
                conn, tablename, column = tuple(parts)
            table = uvicore.db.table(tablename, conn)
        else:
            column = dotcol
            table = query.table
        return (column, table)

    def _build_joins(self, query: Query):
        # No Joins
        if not query.joins: return None

        joins = query.table
        for join in query.joins:
            tablename, lwhere, rwhere, type = join

            #dump('doing joins now')
            #dump(table, left_where, right_where)

            if '.' in tablename:
                conn, tablename = tuple(tablename.split('.'))
                table = uvicore.db.table(tablename, conn)
            else:
                table = uvicore.db.table(tablename)

            # Get actual table and column based on conn.table.column dot notation
            lcolumn, ltable = self._column_parts(lwhere, query)

            # Get actual table and column based on conn.table.column dot notation
            rcolumn, rtable = self._column_parts(rwhere, query)

            if type == 'inner':
                joins = joins.join(
                    right=table,
                    onclause=getattr(ltable.c, lcolumn) == getattr(rtable.c, rcolumn)
                )
            elif type == 'outer':
                joins = joins.outerjoin(
                    right=table,
                    onclause=getattr(ltable.c, lcolumn) == getattr(rtable.c, rcolumn)
                )
        return joins



    def _build_select(self, query: Query):
        selects = []

        if not query.selects and not query.joins:
            # No explicit selects, no joins, return entire table of columns
            return sa.select([query.table])

        if not query.selects and query.joins:
            selects.extend(query.table.columns)
            for join in query.joins:
                tablename = join[0]
                conn = None
                if '.' in tablename:
                    conn, tablename = tuple(tablename.split('.'))
                table = uvicore.db.table(tablename, conn)
                for column in table.columns:
                    selects.append(column.label(sa.sql.quoted_name(tablename + '__' + column.name, True)))

        if query.selects:
            dump(query.selects)
            for select in query.selects:
                table = query.table
                selects.append(table.columns.get(select))


        # if not query.selects and query.joins:
        #     # No explicit selects, but has joins
        #     # Loop table columns + join columns with labels
        #     pass
        # elif query.selects:
        #     # Explitit selects
        #     pass

        return sa.select(selects)



    def _build_where(self, query: Query, wheres: List[Tuple]):
        """Build all wheres"""
        statements = []
        for where in wheres:
            column, operator, value = where
            table = query.table

            # Get actual table and column based on conn.table.column dot notation
            column, table = self._column_parts(column, query)

            # Convert to SQL Alchemy Where
            if type(value) == str and value.lower() == 'null': value = None
            if operator == 'in':
                statements.append(getattr(table.c, column).in_(value))
            elif operator == '!in':
                statements.append(sa.not_(getattr(table.c, column).in_(value)))
            elif operator == 'like':
                statements.append(getattr(table.c, column).like(value))
            elif operator == '!like':
                statements.append(sa.not_(getattr(table.c, column).like(value)))
            else:
                op = self._operator(operator)
                statements.append(op(getattr(table.c, column), value))

        return statements

    def _operator(self, operator: str):
        ops = {
            '=': operators.eq,
            '==': operators.eq,
            '!=': operators.ne,
            '>': operators.gt,
            '<': operators.lt,
        }
        return ops[operator]
