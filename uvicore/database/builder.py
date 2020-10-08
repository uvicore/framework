from __future__ import annotations

import operator as operators
from copy import copy
from typing import Any, Dict, Generic, List, Tuple, TypeVar, Union

import sqlalchemy as sa
from pydantic.utils import Representation
from sqlalchemy.sql import quoted_name

import uvicore
from uvicore.contracts import QueryBuilder as BuilderInterface
from uvicore.support.dumper import dd, dump

B = TypeVar("B")  # Builder Type (DbQueryBuilder or OrmQueryBuilder)
E = TypeVar("E")  # Entity Model

class Column(Representation):
    __slots__ = (
        'sacol',
        'name',
        'alias',
        #'field',
        'connection',
        'table',
        'tablename',
    )
    def __init__(self, sacol: sa.Column, name: str, alias: str, connection: str, table: sa.Table, tablename: str):
        self.sacol = sacol
        self.name = name
        self.alias = alias
        #self.field = field
        self.connection = connection
        self.table = table
        self.tablename = tablename


class Join(Representation):
    __slots__ = (
        'table',
        'tablename',
        'left',
        'right',
        'onclause',
        'alias',
        'method'
    )
    def __init__(self, table: sa.Table, tablename: str, left: Column, right: Column, onclause: sa.sql.expression.BinaryExpression, alias: str, method: str):
        self.table = table
        self.tablename = tablename
        self.left = left
        self.right = right
        self.onclause = onclause
        self.alias = alias
        self.method = method


class Query(Representation):
    __slots__ = (
        'includes',
        'selects',
        'wheres',
        'or_wheres',
        'filters',
        'or_filters',
        'group_by',
        'order_by',
        'limit',
        'offset',
        'keyed_by',
        'relations',
        'joins',
        'table',
    )

    def __init__(self):
        self.includes: List = []
        self.selects: List = []
        self.wheres: List[Tuple] = []
        self.or_wheres: List[Tuple] = []
        self.filters: List[Tuple] = []
        self.or_filters: List[Tuple] = []
        self.group_by: List = []
        self.order_by: List[Tuple] = []
        self.limit: Optional[int] = None
        self.offset: Optional[int] = None
        self.keyed_by: Optional[str] = None
        self.relations: Dict[str, Relation] = {}
        self.joins: List[Join] = []
        self.table: sa.Table


class QueryBuilder(Generic[B, E]):

    def __init__(self):
        self.query = Query()

    @property
    def _connection(self):
        return self._conn

    def where(self, column: Union[str, List[Tuple], Any], operator: str = None, value: Any = None) -> B[B, E]:
        if type(column) == str:
            # A single where as a string
            # .where('column', 'value')
            # .where('column, '=', 'value')
            if not value:
                value = operator
                operator = '='
            self.query.wheres.append((column, operator.lower(), value))
        elif type(column) == tuple:
            # Multiple wheres in one as a List[Tuple]
            # .where([('column', 'value'), ('column', '=', 'value')])
            for where in column:
                # Recursivelly add Tuple wheres
                if len(where) == 2:
                    self.where(where[0], '=', where[1])
                else:
                    self.where(where[0], where[1], where[2])
        else:
            # Direct SQLAlchemy expression
            self.query.wheres.append(column)
        return self

    def or_where(self, wheres: List[Union[Tuple, Any]]) -> B[B, E]:
        # Or where must be a list of tuple as it required at least 2 statements
        # .or_where([('column', 'value'), ('column', '=', 'value')])
        or_where: List[Tuple] = []
        for where in wheres:
            if type(where) == tuple:
                if len(where) == 2:
                    or_where.append((where[0], '=', where[1]))
                else:
                    or_where.append((where[0], where[1].lower(), where[2]))
            else:
                or_where.append(where)
        self.query.or_wheres.extend(or_where)
        return self

    def order_by(self, column: Union[str, List[Tuple], Any], order: str = 'ASC') -> B[B, E]:
        if type(column) == str:
            self.query.order_by.append((column, order.upper()))
        elif type(column) == tuple:
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
        else:
            # Direct SQLAlchemy expression
            self.query.order_by.append(column)
        return self

    def limit(self, limit: int) -> B[B, E]:
        self.query.limit = limit
        return self

    def offset(self, offset: int) -> B[B, E]:
        self.query.offset = offset
        return self

    def sql(self, method: str = 'select') -> str:
        query, saquery = self._build_query('select', copy(self.query))
        return str(saquery)

    def _build_query(self, method: str, query: Query) -> Tuple:
        # Convert our Query into SQLAlchemy query
        #saquery: sa.sql.select = None

        # where
        #   select
        #   update (not in insert)
        #   delete

        # insert will never come into this get() or build function

        if method == 'select':

            # Build .select() query from tables and joins and selectable columns
            saquery = self._build_select(query)

            # Build .select_from() query from tables and joins
            saquery = self._build_from(query, saquery)

            # Build .order_by() query
            saquery = self._build_order_by(query, saquery)

        # Build WHERE AND queries
        if query.wheres:
            where_ands = self._build_where(query, query.wheres)
            saquery = saquery.where(sa.and_(*where_ands))

        # Build WHERE OR queries
        if query.or_wheres:
            where_ors = self._build_where(query, query.or_wheres)
            saquery = saquery.where(sa.or_(*where_ors))

        # Build .group_by() queries
        saquery = self._build_group_by(query, saquery)

        # Build .limit() query
        if query.limit: saquery = saquery.limit(query.limit)

        # Build .offset query
        if query.offset: saquery = saquery.offset(query.offset)

        # Return query and SQLAlchemy query
        return (query, saquery)

    def _build_group_by(self, query: Query, saquery):
        for column in query.group_by:
            column = self._column(column, query)
            saquery = saquery.group_by(column.sacol)
        return saquery

    def _build_order_by(self, query: Query, saquery):
        for order_by in query.order_by:
            if type(order_by) == tuple:
                column = self._column(order_by[0], query).sacol
                order = order_by[1]

                if order == 'DESC':
                    saquery = saquery.order_by(sa.desc(column))
                else:
                    saquery = saquery.order_by(column)
            else:
                # SQLAlchemy expression
                saquery = saquery.order_by(order_by)
        return saquery

    def _build_from(self, query: Query, saquery) -> sa.select.select_from:
        joins = query.table
        for join in query.joins:
            method = getattr(joins, join.method)
            joins = method(right=join.table, onclause=join.onclause)

        # Return SQLAlchemy .select_from() query
        return saquery.select_from(joins)

    def _build_select(self, query: Query) -> sa.select:
        selects = []

        if not query.selects and not query.joins:
            # No explicit selects, no joins, return entire table of columns
            return sa.select([query.table])

        elif not query.selects and query.joins:
            selects.extend(query.table.columns)
            for join in query.joins:
                for column in join.table.columns:
                    selects.append(column.label(quoted_name(join.alias + '__' + column.name, True)))

        elif query.selects:
            # Explicit selects (can be on main table or joined relations)
            for select in query.selects:
                column = self._column(select, query)
                if column.alias:
                    selects.append(column.sacol.label(quoted_name(column.alias, True)))
                else:
                    selects.append(column.sacol)

        # Return SQLAlchemy .select() statment with above columns
        return sa.select(selects)

    def _build_where(self, query: Query, wheres: List[Tuple]):
        """Build all wheres"""
        statements = []
        for where in wheres:
            if type(where) == tuple:
                column, operator, value = where
                column = self._column(column, query).sacol

                # Convert to SQL Alchemy Where
                if type(value) == str and value.lower() == 'null': value = None
                if operator == 'in':
                    statements.append(column.in_(value))
                elif operator == '!in':
                    statements.append(sa.not_(column.in_(value)))
                elif operator == 'like':
                    statements.append(column.like(value))
                elif operator == '!like':
                    statements.append(sa.not_(column.like(value)))
                else:
                    op = self._operator(operator)
                    statements.append(op(column, value))
            else:
                # SQLAlchemy expression
                statements.append(where)

        return statements

    def _pk(self):
        for column in self.query.table.primary_key.columns:
            # Just take first PK for now???
            return str(column.name)

    def _column(self, dotname: Any, query: Query = None) -> Column:
        # Column() class builder from dotname
        if not query: query = self.query
        if dotname is None: return None
        name = dotname
        alias = None
        table = query.table
        tablename = str(table.name)
        conn = self._connection

        if type(dotname) == str:
            # Get column information from a string
            # This is separated into its own method so we can override it with the ORM builder
            table, tablename, column, name, conn = self._column_from_string(dotname, query)

        elif type(dotname) == sa.Column:
            # SQLAlchemy column
            column = dotname
            name = str(column.name)
            table = column.table
            tablename = str(column.table.name)
        else:
            # SQLAlchemy generic function (sa.func.count(), min(), max()...)
            column = dotname
            name = 'func'

        # Set alias only if using column is a relation
        if alias is None:
            if str(table.name) != str(query.table.name):
                alias = str(table.name) + '__' + name

        # Return new column class
        return Column(column, name, alias, conn, table, tablename)

    def _column_from_string(self, dotname: str, query: Query) -> Tuple:
        name = dotname
        table = query.table
        tablename = str(table.name)
        conn = self._connection
        if '.' in dotname:
            parts = dotname.split('.')
            if len(parts) == 2:
                tablename, name = tuple(parts)
            elif len(parts) == 3:
                conn, tablename, name = tuple(parts)

            table = uvicore.db.table(tablename, conn)
            if table is None:
                # Table not found by name, must be a JOIN alias
                for join in query.joins:
                    if join.alias == tablename:
                        table = join.table
                        alias = join.alias + '__' + name
                        break;

        column = table.columns.get(name)
        return (table, tablename, column, name, conn)

    def _operator(self, operator: str):
        ops = {
            '=': operators.eq,
            '==': operators.eq,
            '!=': operators.ne,
            '>': operators.gt,
            '<': operators.lt,
        }
        return ops[operator]


# IoC Class Instance
# No need to IoC this one because it is always inherited
# If you need to overrite it use the IoC to swap DbQueryBuilder or OrmQueryBuilder
# and set a new parent from there.
