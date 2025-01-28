from __future__ import annotations

import operator as operators
from copy import deepcopy
from typing import Any, Dict, Generic, List, Tuple, TypeVar, Union, OrderedDict
from uvicore.support import hash

import sqlalchemy as sa
from sqlalchemy.sql.expression import BinaryExpression

from sqlalchemy.sql import quoted_name
from collections import OrderedDict as ODict
from dataclasses import dataclass

import uvicore
from uvicore.contracts import QueryBuilder as BuilderInterface
from uvicore.support.dumper import dd, dump

B = TypeVar("B")  # Builder Type (DbQueryBuilder or OrmQueryBuilder)
E = TypeVar("E")  # Entity Model


@uvicore.service()
class QueryBuilder(Generic[B, E], BuilderInterface[B, E]):

    def __init__(self):
        self.query = Query()

    def where(self, column: Union[str, BinaryExpression, List[Union[Tuple, BinaryExpression]]], operator: str = None, value: Any = None) -> B[B, E]:
        """Add where statement to query"""
        if type(column) == str or type(column) == sa.Column:
            # A single where as a string or actual SQLAlchemy Column
            # String default =
            #   .where('column', 'value')
            # String explicit operator:
            #   .where('column, '=', 'value')
            # SA Column default =
            #   .where(table.column, 'value')
            # SA Column explicit operator:
            #   .where(table.column, '=', 'value')

            # Swap operator and value
            if not value: value = operator; operator = '='
            self.query.wheres.append((column, operator.lower(), value))
        elif type(column) == list:
            # Multiple wheres in one as a List[Tuple] or List[BinaryExpression]
            for where in column:
                # Recursivelly add Tuple wheres
                if type(where) == tuple:
                    # String
                    #   .where([('column', 'value'), ('column', '=', 'value')])
                    # SA Column
                    #   .where([(table.column, 'value'), (table.column, '=', 'value)])
                    if len(where) == 2:
                        self.where(where[0], '=', where[1])
                    else:
                        self.where(where[0], where[1], where[2])
                else:
                    # SQLAlchemy Binary Expression
                    # .where([table.column == 'value', table.column >= 'value'])
                    self.where(where)
        else:
            # Direct SQLAlchemy expression
            # .where(table.column == 'value' and table.column >= 'value')
            self.query.wheres.append(column)
        return self

    def or_where(self, wheres: List[Union[Tuple, BinaryExpression]]) -> B[B, E]:
        """Add or where statement to query"""
        # Or where must be a list of tuple or BinaryExpression as it requires at least 2 statements
        # .or_where([('column', 'value'), ('column', '=', 'value')])
        # .or_where([table.column == value, table.column == value])
        or_wheres: List[Tuple] = []
        for where in wheres:
            if type(where) == tuple:
                if len(where) == 2:
                    or_wheres.append((where[0], '=', where[1]))
                else:
                    or_wheres.append((where[0], where[1].lower(), where[2]))
            else:
                # SQLAlchemy Binary Expression
                or_wheres.append(where)
        self.query.or_wheres.extend(or_wheres)
        return self

    def order_by(self, column: Union[str, List[str], List[Tuple], Any], order: str = 'ASC') -> B[B, E]:
        """Order results by these columns ASC or DESC order"""
        if type(column) == str:
            # A single order_by as a string or actual SQLAlchemy Column
            # .order_by('column') or .order_by('column', 'DESC')
            # .order_by
            self.query.order_by.append((column, order.upper()))
        elif type(column) == list:
            # Multiple order as a List[Tuple] (column, order)
            for order_by in column:
                if type(order_by) == tuple:
                    if len(order_by) == 1:
                        # Should never hit, because a tuple of (columnx) is actually not a tuple type at all
                        # but if someone added (columnx,) then it is a tuple, and order by should default to ASC
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
            if type(column) == sa.sql.elements.UnaryExpression:
                # If we use SA for order ASC or DESC then column is a UnaryExpression
                # .order_by(posts.id) or .order_by(sa.desc(posts.id)) or .order_by(sa.asc(posts.id))
                self.query.order_by.append(column)
            else:
                # If not UnaryExpression, then we assume column is a true SA colum, and we use our order string
                self.query.order_by.append((column, order))
        return self

    def limit(self, limit: int) -> B[B, E]:
        """Limit results"""
        self.query.limit = limit
        return self

    def offset(self, offset: int) -> B[B, E]:
        """Limit offset"""
        self.query.offset = offset
        return self

    def cache(self, key: str = None, *, seconds: int = None, store: str = None) -> B[B, E]:
        """Cache results, None seconds uses cache backend default, 0=forever"""
        # Seconds as None will default to cache configured default seconds
        self.query.cache = {
            'key': key,
            'seconds': seconds,
            'store': store,
        }
        return self

    def sql(self, method: str = 'select') -> str:
        """Get all SQL queries involved in this query builder"""
        query, saquery = self._build_query('select', self.query.copy())
        return str(saquery)

    def _build_query(self, method: str, query: Query) -> Tuple:
        # Convert our Query into SQLAlchemy query

        # where
        #   select
        #   update (not in insert)
        #   delete

        # insert will never come into this get() or build function
        if method == 'select':
            # Build .select() query from tables, joins and selectable columns
            saquery = self._build_select(query).distinct()

            # Build .select_from() query from tables and joins
            saquery = self._build_from(query, saquery)

            # Build .order_by() query
            saquery = self._build_order_by(query, saquery)

            # Build .group_by() queries
            saquery = self._build_group_by(query, saquery)

            # Build .limit() query
            if query.limit: saquery = saquery.limit(query.limit)

            # Build .offset query
            if query.offset: saquery = saquery.offset(query.offset)

        elif method == 'delete':
            # Build .delete() query from table
            saquery = sa.delete(query.table)

        elif method == 'update':
            # Build .update() query from table
            saquery = sa.update(query.table)

        # Build WHERE AND queries
        if query.wheres:
            where_ands = self._build_where(query, query.wheres)
            saquery = saquery.where(sa.and_(*where_ands))

        # Build WHERE OR queries
        if query.or_wheres:
            where_ors = self._build_where(query, query.or_wheres)
            saquery = saquery.where(sa.or_(*where_ors))

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
        return saquery.select_from(joins)

    def _build_select(self, query: Query) -> sa.select:
        selects = []

        if not query.selects and not query.joins:
            # No explicit selects, no joins, return entire table of columns
            return sa.select(query.table)

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

        # SA 1.4 vs 2.0
        # SA 1.4 allowed LIST of Columns in sa.select(selects)
        # SA 2.0 errors on a LIST and wants positional arguments instead
        # So use pythons * operator to unpack LIST into *arg - sa.select(*selects)

        # Return SQLAlchemy .select() statment with above columns
        return sa.select(*selects)

    def _build_where(self, query: Query, wheres: List[Tuple]):
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

    def _connection(self):
        return self._conn

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
        conn = self._connection()

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
        conn = self._connection()
        dotname = dotname.replace('__', '.')
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
            '>=': operators.ge,
            '<=': operators.le,
        }
        return ops[operator]




# IoC Class Instance
# No need to IoC this one because it is always inherited
# If you need to overrite it use the IoC to swap DbQueryBuilder or OrmQueryBuilder
# and set a new parent from there.


@dataclass
@uvicore.service()
class Column:
    # Private Column dataclass.  Not meant to be imported by any user but not _Column for display purposes
    # in logging and debugging.  I hate _ especially for dataclasses

    # __slots__ = (
    #     'sacol',
    #     'name',
    #     'alias',
    #     #'field',
    #     'connection',
    #     'table',
    #     'tablename',
    # )
    sacol: sa.Column
    name: str
    connection: str
    table: sa.Table
    tablename: str

    def __init__(self, sacol: sa.Column, name: str, alias: str, connection: str, table: sa.Table, tablename: str):
        self.sacol = sacol
        self.name = name
        self.alias = alias
        #self.field = field
        self.connection = connection
        self.table = table
        self.tablename = tablename


@dataclass
@uvicore.service()
class Join:
    # Private Join dataclass.  Not meant to be imported by any user but not _Join for display purposes
    # in logging and debugging.  I hate _ especially for dataclasses

    # __slots__ = (
    #     'table',
    #     'tablename',
    #     'left',
    #     'right',
    #     'onclause',
    #     'alias',
    #     'method'
    # )
    table: sa.Table
    tablename: str
    left: Column
    right: Column
    onclause: BinaryExpression
    alias: str
    method: str

    def __init__(self, table: sa.Table, tablename: str, left: Column, right: Column, onclause: BinaryExpression, alias: str, method: str):
        self.table = table
        self.tablename = tablename
        self.left = left
        self.right = right
        self.onclause = onclause
        self.alias = alias
        self.method = method


@dataclass
@uvicore.service()
class Query:
    # Private Query dataclass.  Not meant to be imported by any user but not _Query for display purposes
    # in logging and debugging.  I hate _ especially for dataclasses

    # __slots__ = (
    #     'includes',
    #     'selects',
    #     'wheres',
    #     'or_wheres',
    #     'filters',
    #     'or_filters',
    #     'group_by',
    #     'order_by',
    #     'sort',
    #     'limit',
    #     'offset',
    #     'keyed_by',
    #     'relations',
    #     'joins',
    #     'table',
    # )
    includes: List
    selects: List
    wheres: List
    or_wheres: List[Tuple]
    filters: List[Tuple]
    or_filters: List[Tuple]
    group_by: List
    order_by: List[Tuple]
    sort: List[Tuple]
    limit: Optional[int]
    offset: Optional[int]
    keyed_by: Optional[str]
    show_writeonly: Union[bool, List]
    cache: Dict
    relations: OrderedDict[str, Relation]
    joins: List[Join]
    table: sa.Table


    def __init__(self):
        self.includes: List = []
        self.selects: List = []
        self.wheres: List[Tuple] = []
        self.or_wheres: List[Tuple] = []
        self.filters: List[Tuple] = []
        self.or_filters: List[Tuple] = []
        self.group_by: List = []
        self.order_by: List[Tuple] = []
        self.sort: List[Tuple] = []
        self.limit: Optional[int] = None
        self.offset: Optional[int] = None
        self.keyed_by: Optional[str] = None
        self.show_writeonly: Union[bool, List] = False
        self.cache: Dict = None
        self.relations: OrderedDict[str, Relation] = ODict()
        self.joins: List[Join] = []
        self.table: sa.Table = None

    def copy(self):
        # Objects are always byref in python.  We want a complete deep clone
        # of a query.  Must use deep or it won't copy the .joins since its a
        # list of an actual class also.  Shallow copies all lists and dicts, but
        # not classes or list of classes, they will be byref unless deep
        table = self.table
        self.table = None
        newquery = deepcopy(self)
        self.table = table

        # Copy the original table by ref back or else SQLAlchemy will see a new
        # table class ID and think you are joining 2 different tables.  We must keep
        # the exact instance of each table.
        newquery.table = table
        return newquery

    def hash(self, *, hash_type: str = 'sha1', **kwargs) -> str:
        """Generate a unique hash for this query.  Used for automatic unique cache strings"""
        unique_params = {
            'tablename': self.table.name,
            'includes': self.includes,
            'selects': [str(col) for col in self.selects],
            'wheres': self.wheres,
            'or_wheres': self.or_wheres,
            'filters': self.filters,
            'or_filters': self.or_filters,
            'group_by': self.group_by,
            'order_by': self.order_by,
            'sort': self.sort,
            'limit': self.limit,
            'offset': self.offset,
            'keyed_by': self.keyed_by,
            'kwargs': kwargs,
        }
        hash_method = getattr(hash, hash_type)
        return hash_method(str(unique_params))

