from __future__ import annotations

import operator as operators
import os

from collections import OrderedDict as ODict
from copy import deepcopy
from typing import Any, Dict, Generic, List, OrderedDict, Tuple, TypeVar, Union, Callable
from uvicore.support.hash import sha1

import sqlalchemy as sa
from sqlalchemy.sql import quoted_name
from sqlalchemy.sql.expression import BinaryExpression

import uvicore
from uvicore.contracts import OrmQueryBuilder as BuilderInterface
from uvicore.database.builder import QueryBuilder, Join, Query
from uvicore.orm.fields import (BelongsTo, BelongsToMany, Field, HasMany,
                                HasOne, MorphMany, MorphOne, MorphToMany)
from uvicore.orm.fields import Relation
from uvicore.support.collection import getvalue
from uvicore.support.dumper import dd, dump

B = TypeVar("B")  # Builder Type (DbQueryBuilder or OrmQueryBuilder)
E = TypeVar("E")  # Entity Model


@uvicore.service()
class OrmQueryBuilder(Generic[B, E], QueryBuilder[B, E], BuilderInterface[B, E]):
    """ORM Query Builder"""

    def __init__(self, entity: E):
        self.entity = entity
        super().__init__()

        # Not all models require tables (databaseless models)
        if entity.table is not None:
            self.query.table = entity.table
        else:
            self.query.table = entity.tablename

    @property
    def log(self):
        return uvicore.log.name('uvicore.orm')

    def _where_dict(self, parent_method: Callable, column: str, operator: str = None, value: Any = None):
        # Not sure I want this code if I can't do where AND and where OR etc...
        # Maybe revisit later.
        found_dict_where = False
        if type(column) == str:
            # Swap operator and value
            if not value: value = operator; operator = '='
            if '.' in column:
                parts = column.split(".")
                if len(parts) == 2:
                    fieldname = parts[0]
                    fieldvalue = parts[1]
                    field = self.entity.modelfields.get(fieldname)  # Don't use modelfield() as it throws exception
                    relation = field.relation.fill(field)
                    if fieldvalue not in relation.entity.modelfields.keys():
                        dict_key = getvalue(relation, 'dict_key')
                        dict_value = getvalue(relation, 'dict_value')
                        if dict_key and type(dict_value) == str:
                            found_dict_where = True

        if found_dict_where:
            # Dict where found, convert to proper where based on dict_key
            return parent_method([
                (fieldname + '.' + dict_key, '=', fieldvalue),
                (fieldname + '.' + dict_value, operator, value)
            ])
            pass
        else:
            # Regular where, pass to parent (builder.py) where
            return parent_method(column, operator, value)

    def where(self, column: Union[str, BinaryExpression, List[Union[Tuple, BinaryExpression]]], operator: str = None, value: Any = None) -> B[B, E]:
        # Custom where just for OrmQueryBuilder only to check for dict_key and dict_value type wheres
        # This is very limited and does not work with ORs or multiple ANDs.  Why not multiple ANDS?  Try querying posts join attributes and
        # where key=x and value=y and key=a and value=b and see what happens (you get nothing).  This is the nature of polymorphic one-to-many
        # So you can where on one attribute with one or more (in) values, but you cannot where to TWO attributes with AND
        # I also cannot do complex ANDs with ORs mixed around yet.
        # Like this is not yet possible in the ORM.  It can only do all ANDs then a final AND (asdf or asdf or asdf)
        # WHERE
        # (attributes.key = 'post1-test1' and attributes.value = 'value for post1-test1')
        # or
        # (attributes.key = 'post2-test1' and attributes.value = 'value for post2-test1')
        return self._where_dict(super().where, column, operator, value)

    def include(self, *args) -> B[B, E]:
        """Include child relation models"""
        # import inspect
        # x = inspect.currentframe()
        # y = inspect.getouterframes(x, 1)
        # context = y[1].code_context
        # #dump(context)
        #args = ['creator.contact']

        # Convert List to Args
        if len(args) == 1 and type(args[0]) == list: args = args[0]

        # Loop each arg and add to query.includes
        for include in args:
            self.query.includes.append(include)
        return self

    def filter(self, column: Union[str, BinaryExpression, List[Union[Tuple, BinaryExpression]]], operator: str = None, value: Any = None) -> B[B, E]:
        """Filter child relationship by this AND clause"""
        # Filters are for Many relations only
        if type(column) == str or type(column) == sa.Column:
            # A single filter as a string or actual SQLAlchemy Column
            # String default =
            #   .filter('column', 'value')
            # String explicit operator:
            #   .filter('column, '=', 'value')
            # SA Column default =
            #   .filter(table.column, 'value')
            # SA Column explicit operator:
            #   .filter(table.column, '=', 'value')

            # Swap operator and value
            if not value: value = operator; operator = '='
            self.query.filters.append((column, operator.lower(), value))
        elif type(column) == list:
            # Multiple filters in one as a List[Tuple] or List[BinaryExpression]
            for filter in column:
                # Recursivelly add Tuple filters
                if type(filter) == tuple:
                    # String
                    #   .filter([('column', 'value'), ('column', '=', 'value')])
                    # SA Column
                    #   .filter([(table.column, 'value'), (table.column, '=', 'value)])
                    if len(filter) == 2:
                        self.filter(filter[0], '=', filter[1])
                    else:
                        self.filter(filter[0], filter[1], filter[2])
                else:
                    # SQLAlchemy Binary Expression
                    # .filter([table.column == 'value', table.column >= 'value'])
                    self.filter(filter)
        else:
            # Direct SQLAlchemy expression
            # .filter(table.column == 'value' and table.column >= 'value')
            self.query.filters.append(column)
        return self

    def or_filter(self, filters: List[Union[Tuple, BinaryExpression]]) -> B[B, E]:
        """Filter child relationship by this OR clause"""
        # Or filter must be a list of tuple or BinaryExpression as it requires at least 2 statements
        # .or_filter([('column', 'value'), ('column', '=', 'value')])
        # .or_filter([table.column == value, table.column == value])
        or_filters: List[Tuple] = []
        for filter in filters:
            if type(filter) == tuple:
                if len(filter) == 2:
                    or_filters.append((filter[0], '=', filter[1]))
                else:
                    or_filters.append((filter[0], filter[1].lower(), filter[2]))
            else:
                # SQLAlchemy Binary Expression
                or_filters.append(filter)
        self.query.or_filters.extend(or_filters)
        return self

    def sort(self, column: Union[str, List[str], List[Tuple], Any], order: str = 'ASC') -> B[B, E]:
        """Sort Many relations only"""
        # This will not work as binary expression, becuase relation name is often
        # different than colums tablename
        if type(column) == str or type(column) == sa.Column:
            # A single sort as a string
            self.query.sort.append((column, order.upper()))
        else:
            # Multiple sort in one as List or List[Tuple]
            for sort in column:
                if type(sort) == tuple:
                    if len(sort) == 2:
                        self.sort(sort[0], sort[1])
                    else:
                        self.sort(sort[0], 'ASC')
                else:
                    self.sort(sort, 'ASC')
        return self

    def key_by(self, field: str) -> B[B, E]:
        """Key results as a Dictionary by this column"""
        self.query.keyed_by = field
        return self

    def show_writeonly(self, fields: List = None):
        if fields is None:
            self.query.show_writeonly = True
        else:
            self.query.show_writeonly = fields
        return self

    def sql(self, method: str = 'select', queries: List = None) -> str:
        """Get all SQL queries involved in this ORM statement"""
        if queries is None: queries = self._build_orm_queries(method)
        sqls = {}
        for query in queries:
            #sqls += '-- ' + query.get('name').upper() + ':' + os.linesep + query.get('sql') + os.linesep + os.linesep
            sqls[query.get('name')] = query.get('sql').replace('\n', '')
        return sqls

    def queries(self, method: str = 'select') -> List:
        """Get all queries involved in this ORM statement"""
        return self._build_orm_queries('select')

    async def find(self, pk_value: Union[int, str] = None, **kwargs) -> Union[E, None]:
        """Execute query by primary key or custom column and return first row found"""
        if pk_value:
            column = self._pk()
            value = pk_value
        elif kwargs:
            column = [x for x in kwargs.keys()][0]
            value = [x for x in kwargs.values()][0]

        # Ensure some incompatible builder methods are reset
        self.query.wheres = []
        self.query.or_wheres = []
        self.query.order_by = []
        self.query.keyed_by = None

        # Add in where on PK
        self.where(column, value)

        # Get List of Entities based on query results
        entities = await self.get()

        # Return one record or None
        if entities: return entities[0]
        return None

    async def get(self) -> Union[List[E], Dict[str, E]]:
        """Execute a select query and return all rows found"""

        # Get this models connection configuration
        #connection = uvicore.db.connection(self._connection())
        #backend = connection.backend
        #if backend != 'sqlalchemy':
            # Using a custom, non sqlalchemy backend.  Could be an API, CSV, JSON...
            # Load up the custom backend and fire off the get() executor
            #dump('not sqlalchemy')

        # Build SQLAlchemy select queries
        queries = self._build_orm_queries('select')

        self.log.nl().header('Queries')
        self.log.dump(queries)

        self.log.header('Raw SQL Queries')
        self.log.info(self.sql('select', queries))

        # Get hook?  Experimental
        # FIXME
        if hasattr(self.entity, 'get'):
            return await self.entity.get(queries)

        # Detect caching
        cache = self.query.cache
        if cache:
            prefix = 'uvicore.orm/'
            if cache.get('key') is None:
                # No cache name specified, automatically build unique based on queries
                query_hash = ''
                for query in queries:
                    if query['name'] == 'main':
                        query_hash = query.get('query').hash(
                            hash_type='sha1',
                            package='uvicore.orm',
                            entity=self.entity,
                            connection=self._connection()
                        )
                        break
                cache['key'] = prefix + query_hash
                #dump(query_hash)
            else:
                cache['key'] = prefix + cache.get('key')

        if cache and await uvicore.cache.has(cache.get('key')):
            # Cache found, use cached results
            #dump('ORM FROM CACHE')
            entities = await uvicore.cache.get(cache.get('key'))
        else:
            # Execute each query
            results = None
            main_query = None
            has_many = {}
            for query in queries:
                if query.get('name') == 'main':
                    main_query = query.get('query')
                    results = await self.entity.fetchall(query.get('saquery'))
                else:
                    has_many[query.get('name')] = await self.entity.fetchall(query.get('saquery'))

            # Convert results to List of entities
            entities = self._build_orm_results(main_query, results, has_many)

            # Add to cache if desired
            if cache: await uvicore.cache.put(cache.get('key'), entities, seconds=cache.get('seconds'))

        # Return List of Entities
        return entities

    async def delete(self) -> None:
        """Execute delete query"""

        # Build SQLAlchemy delete query
        query, saquery = self._build_query('delete', self.query.copy())

        # Execute query
        await self.entity.execute(saquery)

    async def update(self, **kwargs) -> None:
        """Execute update query"""

        # Build SQLAlchemy delete query
        query, saquery = self._build_query('update', self.query.copy())

        # Add in values
        saquery = saquery.values(**kwargs)

        # Execute query
        await self.entity.execute(saquery)

    def _build_orm_queries(self, method: str) -> List:
        # Different than the single _build_query in the DB Builder
        # This one is for ORM only and build multiple DB queries from one ORM query.
        queries = []

        # First query
        query = self.query.copy()

        # Build relation (join) queries
        self._build_orm_relations(query)

        # Add all columns from main model
        query.selects = self.entity.selectable_columns(show_writeonly=self.query.show_writeonly)

        # Add all selects where any nested relation is NOT a *Many
        relation: Relation
        for relation in query.relations.values():
            if not relation.contains_many(query.relations):
                # Don't use the relation.entity table to get columns, use the join aliased table
                table = self._get_join_table(query, alias=relation.name)
                columns = relation.entity.selectable_columns(table, show_writeonly=self.query.show_writeonly)
                for column in columns:
                    query.selects.append(column.label(quoted_name(relation.name + '__' + column.name, True)))

        # Build first query
        saquery = None
        if query.table is not None:
            query, saquery = self._build_query(method, query)
        queries.append({
            'name': 'main',
            'query': query,
            'saquery': saquery,
            'sql': str(saquery) if saquery is not None else '',
        })

        # So we have our first query perfect
        # Now we need to build a second or more queries for all *Many relations
        relation: Relation
        for relation in query.relations.values():
            # Only handle *Many relations
            if not relation.is_many(): continue

            # Relation __ name converted to dot name
            rel_dot = relation.name.replace('__', '.')

            # New secondary relation query
            query2 = self.query.copy()

            # Build ORM Relations but force HasMany joins to INNER JOIN
            self._build_orm_relations(query2)

            # Only if Many-To-Many add in the main tables pivot ID
            if type(relation) == BelongsToMany or type(relation) == MorphToMany:
                # Bug found while grabbing the table by name.  What if we join the same table twice (though different tables of course)
                # There will be 2 joins with the same table name and _get_join_table will grab the first one in error.
                # Instead we need to use the table alias name + __pivot to grab the proper unique table
                #join_table = self._get_join_table(query2, relation.join_tablename)  # No, using table name will clash if joining multiples of the same table,
                join_table = self._get_join_table(query2, alias=relation.name + '__pivot')  # Relation.name is the alias name which should match the unique join table even if multiples
                query2.selects.append(
                    getattr(join_table.c, relation.left_key).label(
                        quoted_name(relation.name + '__' + relation.left_key, True)
                    )
                )

            # Set selects to only those in the related table
            table = self._get_join_table(query2, alias=relation.name)
            columns = relation.entity.selectable_columns(table, show_writeonly=self.query.show_writeonly)
            for column in columns:
                query2.selects.append(column.label(quoted_name(relation.name + '__' + column.name, True)))

            # Add in selects for any *One sub_relations
            for sub_relation in query2.relations.values():
                if relation.name + '__' not in sub_relation.name: continue
                if sub_relation.contains_many(query2.relations, skip=relation.name.split('__')): continue
                table = self._get_join_table(query2, alias=sub_relation.name)
                columns = sub_relation.entity.selectable_columns(table, show_writeonly=self.query.show_writeonly)
                for column in columns:
                    query2.selects.append(column.label(quoted_name(sub_relation.name + '__' + column.name, True)))

            # Remove any wheres for this relation.  Why?  Because the relation
            # where is applied to the main query not to relations.  We still
            # show all relations for any main query item
            # If you want to filter relations, use .filter() instead
            new_wheres = []
            for where in query2.wheres:
                # This also matches any sub-relations uder the where and removes those too
                # BROKEN if using SQLAlchemy binary expressions
                # .where(section.name, 'Production')
                if '.' in where[0]:
                    # Perhaps the ORM should not be "hybrid" and always use string dotnotation?
                    where_entity = '.'.join(where[0].split('.')[0:-1]).lower()
                    if rel_dot[0:len(where_entity)] == where_entity:
                        # Found where for this relation or a sub-relation
                        # Notice I continue, therefore I am removing this relations where
                        continue
                new_wheres.append(where)
            query2.wheres = new_wheres

            # Add .filter() as .where()
            query2.wheres.extend(query2.filters)

            # Add .or_filter() as .or_where()
            query2.or_wheres.extend(query2.or_filters)

            # Add where to show only joined record that were found
            # Cant use INNER JOIN instead because it would limit further sub many-to-many
            query2.wheres.append((relation.name + '.' + relation.entity.pk, '!=', None))

            # Swap .sort() that apply to this relation as an order_by
            # This WIPES out any .order_by as they do not apply to relation queries
            new_sorts = []
            for sort in query2.sort:
                (sort_column, sort_order) = sort
                if '.'.join(sort_column.split('.')[0:-1]).lower() == rel_dot.lower():
                    # Found sort for this relation
                    new_sorts.append(sort)
            query2.sort = new_sorts
            query2.order_by = query2.sort

            # Build secondary relation query
            query2, saquery2 = self._build_query(method, query2)
            queries.append({
                'name': relation.name,
                'query': query2,
                'saquery': saquery2,
                'sql': str(saquery2),
            })

        # Return all queries
        return queries

    def _build_orm_relations(self, query: Query) -> None:
        if not query.includes: return

        def extract(field, value):
            entity = None
            foreign = 'id'
            local = field.name + '_id'
            if type(value) == tuple:
                entity = value[0]
                if len(value) >= 2:
                    foreign = value[1]
                if len(value) == 3:
                    local = value[2]
            else:
                entity = value
            return entity, foreign, local

        # Loop each 'include' string and JOIN in proper child relation tables
        relations: OrderedDict[str, Relation] = ODict()
        for include in query.includes:

            # Includes are in dotnotation form (creator.info, posts.comments etc...)
            # Each part (.) is a table and nested child tables.  Split out each part.
            parts = [include]
            if '.' in include: parts = include.split('.')

            # Each separate include (including all parts in that include) walk down in entities
            # starting with the main model entity (self.entity).  So for each include, start at the main entity.
            entity = self.entity

            # Loop each "include part" as each are nested tables with joins
            parts_added = []
            for part in parts:

                # Get field for this "include part".  Remember entity here is not self.entity, but a walkdown
                # based on each part (separated by dotnotation)
                field: Field = entity.modelfields.get(part)  # Don't use modelfield() as it throws exception

                # Field not found, include string was a typo
                if not field: continue

                # Field has a column entry, which means its NOT a relation
                if field.column: continue

                # Field is not an actual relation
                if not field.relation: continue

                # Keep track of parts we have already completed
                parts_added.append(part)

                # Relation name is a __ join of all parts walked thus far
                relation_name = '__'.join(parts_added)

                # Get actual relation object
                relation = field.relation.fill(field)

                # Set a new name based on relation_name dot notation for nested relations
                relation.name = relation_name

                # Add relation to List only once
                if relation_name not in relations:
                    # We have to deepcopy a relationship becuase if we have owner and creator
                    # and both of those user models have a "Contact" model, that contact model is a
                    # single instance.  We want separate instances of each relationship
                    relations[relation_name] = deepcopy(relation)

                    # Alias the Joined Table (so we can join the same table multiple times if needed, like owner and creator)
                    # Alias is always the relation_name, we'll just make it doubly clear with its own variable
                    alias=relation_name

                    # Get the table we are joining on (the left table)
                    # If this is the first loop in a "include part", the left_table is the entity table (still walking down)
                    # After that its the previous aliased table
                    left_table = entity.table
                    if len(parts_added) > 1:
                        # Get the table from the join based on all but last part of relation_name
                        left_tablename = '__'.join(relation_name.split('__')[0:-1])
                        left_table = self._get_join_table(query, alias=left_tablename)

                    # Get the join (right) table
                    join_table = relation.entity.table
                    if join_table.name != alias:
                        join_table = sa.alias(relation.entity.table, name=alias)

                    # Many-To-Many
                    if type(relation) == BelongsToMany or type(relation) == MorphToMany:
                        # We have to join 2 tables in a many-to-many
                        # First the relation table (sometimes called intermediate or pivot table)
                        # Second the actual related table
                        # No need to alias *Many joins like we do *One joins because it will never be done twice

                        # Get our pivot (middle) join table
                        # Needs to be an auto incremented ALIAS in case we join the same table twice (user creator and owner...)
                        pivot_join_table = sa.alias(relation.join_table) # Notice no name=alias, just let it append _1, _2... for pivot

                        # Join the *Many Pivot Table
                        left = self._column(getattr(left_table.c, entity.pk))
                        right = self._column(getattr(pivot_join_table.c, relation.left_key))
                        join = Join(
                            table=pivot_join_table,
                            tablename=relation.join_tablename,
                            left=left,
                            right=right,
                            onclause=left.sacol == right.sacol,
                            alias=alias + '__pivot',
                            method='outerjoin'
                        )
                        query.joins.append(join)

                        # Now join the relation/intermediate/pivot table with the related table
                        left = self._column(getattr(pivot_join_table.c, relation.right_key))
                        right = self._column(getattr(join_table.c, relation.entity.pk))
                        join = Join(
                            #table=relation.entity.table,
                            table=join_table,
                            tablename=relation.entity.tablename,
                            left=left,
                            right=right,
                            onclause=left.sacol == right.sacol,
                            alias=alias,
                            method='outerjoin'
                        )
                        query.joins.append(join)

                    else:
                        # These One-To-One or One-To-Many on the BelongsTo side can be joined
                        # Multiple times.  For exampel post creator and post owner both join User table
                        # So they require aliases

                        # Debug dump which tables are which
                        #dump('relation_name: ' + relation_name + ' - main table: ' + left_table.name + ' - join_table: ' + join_table.name + ' - alias: ' + alias)

                        # Map relation.local_key and foreign_key Field names to column names
                        #local_key = relation.entity.mapper(relation.local_key).column()
                        #foreign_key = relation.entity.mapper(relation.foreign_key).column()
                        local_key = relation.local_key
                        foreign_key = relation.foreign_key

                        # Join condition columns
                        left = self._column(getattr(left_table.c, local_key))
                        right = self._column(getattr(join_table.c, foreign_key))

                        # Onclause, default for most relations
                        onclause = left.sacol == right.sacol

                        # Onclause override for Polymorphic relations
                        if type(relation) == MorphOne or type(relation) == MorphMany:
                            # In polymorphic, add the entity type to the onclause using and_
                            # Purpose is to get this JOIN ON AND CLAUSE
                            # ...JOIN attributes ON attributable_type = 'posts' AND id = attributable_id

                            # Get the ploy_type column (ex: attributable_type)
                            poly_type = self._column(getattr(join_table.c, relation.foreign_type))

                            # That 'posts' is the actual posts table.  But sometimes the table is an Alias
                            # like 'post' (singular).  So we need to use _get_tablename to get the REAL tablename even an Alias

                            # poly_type.sacol is 'attributable_type'
                            # self.get_tablename(left.table) is 'posts'
                            # left.sacol is 'id'
                            # right.sacol is 'attributable_id'
                            onclause = sa.and_(poly_type.sacol == self._get_tablename(left.table), left.sacol == right.sacol)

                        # Append new Join
                        join = Join(
                            table=join_table,
                            tablename=str(join_table.name),
                            left=left,
                            right=right,
                            onclause=onclause,
                            alias=alias,
                            method='outerjoin'
                        )
                        query.joins.append(join)


                    # All other types of relations
                    # elif type(relation) == HasMany:
                    #     # The One-To-Many on the HasMany side will never be joined
                    #     # twice and therefore do not need aliases
                    #     dump('hi')

                    #     # Join condition columns
                    #     left = self._column(getattr(entity.table.c, relation.local_key))
                    #     right = self._column(getattr(relation.entity.table.c, relation.foreign_key))

                    #     # Append new Join
                    #     join = Join(
                    #         table=relation.entity.table,
                    #         tablename=str(relation.entity.table.name),
                    #         left=left,
                    #         right=right,
                    #         onclause=left.sacol == right.sacol,
                    #         alias=relation_name,
                    #         method='outerjoin'
                    #     )
                    #     query.joins.append(join)

                    # Add joins only for one-to-one or one-to-many inverse
                    # Outer Join in case some foreign keys are nullable
                    #if field.has_one or field.belongs_to:
                    #if query.joins is None: query.joins = entity.table
                    #query.joins = query.joins.outerjoin(
                    #    right=relation.entity.table,
                    #    onclause=getattr(entity.table.c, relation.local_key) == getattr(relation.entity.table.c, relation.foreign_key)
                    #)

                # Walk down each "include parts" entities
                entity = relation.entity

        # Set query.relations
        query.relations = relations

    def _build_orm_results(self, query: Query, primary: List, secondary: Dict = {}) -> List[E]:
        # No primary results, return empty List
        if not primary: return []

        self.log.nl().header('Relations')
        self.log.dump(query.relations)

        self.log.nl().header('Primary Results')
        self.log.dump(primary)

        self.log.nl().header('Has Many Data')
        self.log.dump(secondary)

        # Deepcopy relations Dict so I can remove relations I have already processed.
        # I process all secondary results first.  This means all left over relations are of
        # the primary results
        relations = deepcopy(query.relations)

        # Dictionary of all secondary converted models
        models = {}

        # Dictionary of all *One models as a cache to deduplicate class instantiation
        singles = {}

        # Full any *One relations method
        def fill_one_relations(rel_name: str, data: List):
            """Fill only the *One relations (One-To-One, One-To-Many)"""
            self.log.nl().header('Filling *One Relations for ' + rel_name)

            # Skip if no data
            if not data:
                #models[rel_name] = {}
                return

            # Determin if data is primary or secondary
            primary = (rel_name == 'primary')

            # Split rel_name into __ parts
            rel_name_parts = rel_name.split('__')

            # Get the actual field, relation and entity for this relation rel_name
            entity = self.entity
            if not primary:
                for rnpart in rel_name_parts:
                    field: Field = entity.modelfield(rnpart)
                    entity = field.relation.fill(field).entity

            #self.log.item('Field: ' + str(field))
            self.log.item('Entity: ' + str(entity))
            self.log.item('Data Keys: ' + str(list(data[0]._mapping.keys())))

            # Add a new List to our Dict of models
            models[rel_name] = {}

            # Pk field and column
            pk = entity.pk
            pk_column = entity.mapper(pk).column()
            if not primary: pk_column = rel_name + '__' + pk_column

            # Track completed relations so I can remove from our relations list later
            completed_relations = {}

            # Loop each row of raw data
            i = 0
            for row in data:

                # Because of Many-To-Many we could have the same model multiple times.  But we only want
                # to convert and deal with it once based on unique PK
                if getattr(row, pk_column) in models[rel_name]: continue
                #if models[rel_name][getattr(row, pk_column)]: continue

                # Convert this one row to model (just the main fields, not relations)
                if primary:
                    root_model = entity.mapper(row).model()
                    #root_model = entity.mapper(row).row_to_model()
                else:
                    root_model = entity.mapper(row, rel_name).model()
                    #root_model = entity.mapper(row, rel_name).row_to_model()

                # Get pk value
                pk_value = getattr(root_model, pk)

                # Loop only *One relations that apply to this one "data" model
                relation: Relation
                for relation in relations.values():

                    # Only look at relations that begin with this relation__ and are *One
                    if not primary and rel_name + '__' not in relation.name: continue

                    # Walk up relations and exclude if ANY relation is a *Many starting from rel_name and up
                    if relation.contains_many(query.relations, skip=rel_name_parts): continue

                    # Log output
                    if i == 0: self.log.item('Relation: ' + relation.name + ' - ' + str(relation))

                    # RowProxy results lookup prefix
                    prefix = relation.name

                    # Get all relation fieldnames from relation.name split
                    fieldnames = relation.name.split('__')
                    if not primary:
                        # Skip the first __ parts of rel_name
                        fieldnames = fieldnames[len(rel_name_parts):]
                    if i == 0: self.log.item2('  Fieldnames: ' + ', '.join(fieldnames))

                    # Walk down the root model by fieldnames until you reach the nested
                    # model that has the right field to hold this converted sub model
                    # Remember each relation has the full__nested__name so always start with the
                    # root_model for each relation and work your way down.
                    model = root_model
                    for f in range(0, len(fieldnames) - 1):
                        model = getattr(model, fieldnames[f])

                    # Actual fieldname is always the LAST of the fieldnames, but our model was walked down.
                    fieldname = fieldnames[-1] if fieldnames else relation.name

                    # Walkdown Log
                    if i == 0: self.log.item2('  Model Field: ' + fieldname)
                    if i == 0: self.log.item2('  Field Model: ' + str(model.__class__))

                    # Convert this one rows relation data into a sub_relation model
                    # Only convert each unique *One record just once, or else pull from singles cache
                    # The odd part about this cache is if you include many nested relations one one parent model
                    # And a child model also uses the same child, it too will include all nested relations
                    # Example if you do .include('creator.info', 'owner').  If owner is id=1 and id=1 was already
                    # a creator, that owner will also have the nested INFO filled out, because it pulls from the cache.
                    if relation.entity.tablename not in singles: singles[relation.entity.tablename] = {}
                    sub_model_pk = relation.name + '__' + relation.entity.mapper(relation.entity.pk).column()
                    sub_model_pk_value = getattr(row, sub_model_pk)
                    if sub_model_pk_value is not None and sub_model_pk_value not in singles[relation.entity.tablename]:
                        singles[relation.entity.tablename][sub_model_pk_value] = relation.entity.mapper(row, prefix).model()
                        #singles[relation.entity.tablename][sub_model_pk_value] = relation.entity.mapper(row, prefix).row_to_model()

                    # Get sub_model from singles cache
                    if sub_model_pk_value is not None:
                        sub_model = singles[relation.entity.tablename][sub_model_pk_value]
                        #sub_model = relation.entity.mapper(row, prefix).model(False) # No cache version

                        # Add this converted sub_model to the walked down parent model
                        setattr(model, fieldname, sub_model)

                    # Mark relation as complete so I can delete from relations Dict later
                    completed_relations[relation.name] = 1

                # All *One relations have been converted and merged
                # Add this fully converted (including nested *One relations) model to List of models
                models[rel_name][pk_value] = root_model
                i += 1

            # Delete all completed relations from our relation deepcopy.  We will not need them again
            for completed_relation in completed_relations.keys():
                del relations[completed_relation]

        # Fill in all *One relations for all secondary results first.
        # as each relation is merged it will be removed from our local relations deepcopy.
        # All relations left will be those on the main results data.
        for rel_name, rel_data in secondary.items():
            fill_one_relations(rel_name, rel_data)
        #fill_one_relations(secondary['comments'], 'comments')

        # Fill in all *One relations for the primary results.
        fill_one_relations('primary', primary)

        # All relations left should be of *Many either for the primary results
        # or for any of the secondary results
        self.log.nl().header('Leftover Relations are *Many')
        self.log.dump(relations)

        # All records in models Dict are *Many and the main Primary dataset
        # All remaining relations are the *Many which should match the models Dict key
        # Looping the *Many relations in REVERSE gives us the deepest relations first which is critical
        self.log.nl().header('Combining Recursive *Many Models')

        relation: Relation
        for relation in reversed(relations.values()):

            # Relation name parts
            relation_parts = relation.name.split('__')
            field = relation_parts[-1]

            # If models does not contain this relation, skip the merge
            if relation.name not in models: continue

            # Get parent and child Dict of models
            children_name = relation.name
            children = models[relation.name]
            parents_name = 'primary'
            if len(relation_parts) > 1: parents_name = '__'.join(relation_parts[:-1])
            if parents_name in models:
                # Parent is a *Many so grab from models
                parents = models[parents_name]
            else:
                # Parent is a *One, so grap from singles cache
                parents = singles[query.relations.get(parents_name).entity.tablename]

            self.log.item('Combining child: ' + children_name + ' into parent: ' + parents_name)

            # Determine if child *Many results should be displayed as a Dict or List
            dict_key = getvalue(relation, 'dict_key')
            dict_value = getvalue(relation, 'dict_value')
            list_value = getvalue(relation, 'list_value')

            # Loop parents so we can at least set each child to empty [] instead of None.  We always want [] instead of None for empty children
            for parent in parents.values():
                # Set empty [] or {}
                if dict_key:
                    setattr(parent, field, {})
                else:
                    setattr(parent, field, [])

            # Merge in Many-To-Many by using the original RowProxy result which contains
            # The pivot tables joining column (left_key)
            if type(relation) == BelongsToMany or type(relation) == MorphToMany:
                #left_key = relation.name + '__' + relation.left_key
                left_key = relation.name + '__' + relation.entity.mapper(relation.left_key).field()
                right_key = relation.name + '__' + relation.entity.mapper(relation.entity.pk).column()

                # QUESTION, what is the differente from children.values() vs
                # secondary?  Look at the ELSE below that for child in children.values()
                # but this many* uses secondary?
                # Can I combine all relations into one large loop?
                # Because I am doing identical work in the dict_key stuff

                # ALSO all of this dict_key code may not work anyway
                # I bet the API will not know how to handle input and complain?
                # I may have to handle specially in the ModelRouter

                # Loop raw RowProxy to find proper pivot keys
                for row in secondary[relation.name]:
                    left_id = getattr(row, left_key)
                    right_id = getattr(row, right_key)

                    # Get parent value, the value of the main table
                    parent = parents[left_id]

                    # Get child value. The value of the many record
                    child = children[right_id]

                    # Set None field to empty List
                    if getattr(parent, field) is None:
                        setattr(parent, field, [])

                    # Add each *Many model as a Dict
                    if dict_key:
                        if dict_value:
                            if type(dict_value) == list:
                                value = {key:getattr(child, key) for key in dict_value}
                            else:
                                value = getattr(child, dict_value)
                        else:
                            value = child.dict()
                        getattr(parent, field)[getattr(child, dict_key)] = value


                    # Add each *Many model as a List of a single value
                    elif list_value:
                        getattr(parent, field).append(getattr(child, list_value))

                    # Add each *Many as a List of the actual Models
                    else:
                        # Append to list using deepcopy
                        getattr(parent, field).append(
                            # We must deep copy the record becuase we dedup the *Many
                            # but they could be used multiple times
                            # ?? Hum maybe not, good if you change one it changes them all
                            # But all the *One will NOT be like this I don't believe, have to test
                            #deepcopy(child[right_id])
                            child
                        )

            else:

                for child in children.values():
                    parent_pk_value = getattr(child, relation.entity.mapper(relation.foreign_key).field())
                    if parent_pk_value not in parents: continue;

                    parent = parents[parent_pk_value]
                    field = relation_parts[-1]

                    # # Set None field to empty list
                    # if getattr(parent, field) is None:
                    #     setattr(parent, field, [])

                    # DUPLCATING work here, see above for nearly exact same thing
                    # need to optimize this code

                    # Add each *Many model as a Dict
                    if dict_key:
                        if dict_value:
                            if type(dict_value) == list:
                                # Dict value is a list.  Create a dictionary from the lists keys
                                value = {key:getattr(child, key) for key in dict_value}
                            else:
                                # Dict value is a string, use just that fields value
                                value = getattr(child, dict_value)
                        else:
                            # No dict value set, but there is a dict_key, so we want a dict.  Use the entire record as a dict
                            value = child.dict()
                        getattr(parent, field)[getattr(child, dict_key)] = value
                        #setattr(parent, field, 'x')

                    # Add each *Many model as a List of a single value
                    elif list_value:
                        getattr(parent, field).append(getattr(child, list_value))

                    # Add each *Many as a List of the actual Models
                    else:
                        getattr(parent, field).append(child)


        self.log.nl().header('Singles Cache')
        self.log.dump(singles)

        self.log.nl().header('Secondary *Many Models')
        self.log.dump(models)

        # These models are already a Dict keyed by PK
        # Return existing primary model if user wanted keyby id
        if query.keyed_by == self.entity.pk:
            return models['primary']

        # Key results by another column
        if query.keyed_by:
            keyed_entities = {}
            for entity in models['primary'].values():
                keyed_entities[getattr(entity, self.query.keyed_by)] = entity

            # Return Dictionary of Entities
            return keyed_entities

        # No keyby, convert primary models to a List
        return [x for x in models['primary'].values()]

    def _connection(self):
        return self.entity.connection

    def _pk(self):
        return self.entity.pk

    def _column_from_string(self, dotname: str, query: Query) -> Tuple:
        if '.' in dotname:
            parts = dotname.split('.')
            relation = query.relations.get('__'.join(parts[:-1]))
            table = self._get_join_table(query, alias=relation.name)  # Get table from join alias since its a relation
            field = parts[-1]
            name = self.entity.mapper(field).column()
        else:
            name = self.entity.mapper(dotname).column()
            table = query.table

        tablename = str(table.name)
        column = table.columns.get(name)
        return (table, tablename, column, name, self._connection())

    def _get_join_table(self, query: Query, alias: str):
        """Get the join table for this table alias"""
        for join in query.joins:
            if join.alias == alias:
                return join.table

        # No, found that we ALWAYS want by alias to prevent grabbing the wrong duplicate named table
        # Aliases are always unique
        # if tablename is not None:
        #     for join in query.joins:
        #         if join.tablename == tablename:
        #             return join.table

        #     # Not found by name, check alias
        #     for join in query.joins:
        #         if join.alias == tablename:
        #             return join.table

    def _get_tablename(self, table: Union[sa.Table, sa.sql.selectable.Alias]):
        """Get the REAL tablename even if the table is an Alias"""
        if type(table) == sa.sql.selectable.Alias:
            return table.original.name
        else:
            return table.name

# IoC Class Instance
#_OrmQueryBuilderIoc: _OrmQueryBuilder = uvicore.ioc.make('OrmQueryBuilder', _OrmQueryBuilder)

# Actual Usable Model Class Derived from IoC Inheritence
#class OrmQueryBuilder(Generic[B, E], _OrmQueryBuilderIoc[B, E], BuilderInterface[B, E]):
    #pass
