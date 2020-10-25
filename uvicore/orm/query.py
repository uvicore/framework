from __future__ import annotations

import operator as operators
import os
from collections import OrderedDict as ODict
from copy import deepcopy
from typing import Any, Dict, Generic, List, Tuple, TypeVar, Union, OrderedDict

import sqlalchemy as sa
from pydantic.utils import Representation
from sqlalchemy.sql import quoted_name

import uvicore
from uvicore import log
from uvicore.contracts import OrmQueryBuilder as BuilderInterface
from uvicore.database.builder import Column, Join, Query, QueryBuilder
from uvicore.orm.fields import (BelongsTo, BelongsToMany, Field, HasMany,
                                HasOne, Relation)
from uvicore.support.dumper import dd, dump

B = TypeVar("B")  # Builder Type (DbQueryBuilder or OrmQueryBuilder)
E = TypeVar("E")  # Entity Model

class _OrmQueryBuilder(Generic[B, E], QueryBuilder[B, E]):
    """ORM Query Builder"""

    def __init__(self, entity: E):
        self.entity = entity
        super().__init__()
        self.query.table = entity.table
        #self.query.joins = None

    def include(self, *args) -> QueryBuilder[B, E]:
        # import inspect
        # x = inspect.currentframe()
        # y = inspect.getouterframes(x, 1)
        # context = y[1].code_context
        # #dump(context)
        #args = ['creator.contact']
        for include in args:
            self.query.includes.append(include)
        return self

    def filter(self, column: Union[str, List[Tuple]], operator: str = None, value: Any = None) -> B[B, E]:
        # Filters are for Many relations only
        if type(column) == str:
            # A single filter as a string
            # .filter('relation.column', 'value')
            # .filter('relation.column, '=', 'value')
            if not value:
                value = operator
                operator = '='
            #self.filters.append((column, operator.lower(), value))
            self.query.filters.append((column, operator.lower(), value))
        else:
            # Multiple filters in one as a List[Tuple]
            # .filter([('relation.column', 'value'), ('relation.column', '=', 'value')])
            for filter in column:
                # Recursivelly add Tuple filters
                if len(filter) == 2:
                    self.filter(filter[0], '=', filter[1])
                else:
                    self.filter(filter[0], filter[1], filter[2])
        return self

    def sort(self, column: Union[str, List[Tuple], Any], order: str = 'ASC') -> B[B, E]:
        # Sorts are for Many relations only
        if type(column) == str:
            self.query.sort.append((column, order.upper()))
        elif type(column) == tuple:
            # Multiple sort as a List[Tuple] (column, order)
            for sort in column:
                if type(sort) == tuple:
                    if len(sort) == 1:
                        column = sort[0]
                        order = 'ASC'
                    elif len(sort) == 2:
                        column, order = sort
                else:
                    column = sort
                    order = 'ASC'
                self.sort(column, order)
        else:
            # Direct SQLAlchemy expression
            self.query.sort.append(column)
        return self

    def key_by(self, field: str) -> B[B, E]:
        self.query.keyed_by = field
        return self

    async def link(self, relation: str, values: List) -> None:
        # NOT YET IN INTERFACE
        dump('hiii')

    def sql(self, method: str = 'select', queries: List = None) -> str:
        """Get all SQL queries involved in this ORM statement"""
        if queries is None: queries = self._build_orm_queries(method)
        sqls = ''
        for query in queries:
            sqls += '-- ' + query.get('name').upper() + ':' + os.linesep + query.get('sql') + os.linesep + os.linesep
        return sqls

    def queries(self, method: str = 'select') -> List:
        """Get all queries involved in this ORM statement"""
        return self._build_orm_queries('select')

    async def find(self, pk_value: Any) -> Union[E, None]:
        # Add in where on PK
        self.where(self._pk(), pk_value)

        # Get List of Entities based on query results
        entities = await self.get()

        # Return one record or None
        if entities: return entities[0]
        return None

    async def get(self) -> Union[List[E], Dict[str, E]]:
        queries = self._build_orm_queries('select')
        log.header('Raw SQL Queries')
        log.info(self.sql('select', queries))

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

        # Return List of Entities
        return entities

    def _build_orm_queries(self, method: str) -> List:
        # Different than the single _build_query in the DB Builder
        # This one is for ORM only and build multiple DB queries from one ORM query.
        queries = []

        # First query
        query = self.query.copy()
        self._build_orm_relations(query)

        #dump(query.relations)

        # Add all columns from main model
        query.selects = self.entity.selectable_columns()

        # Add all selects where any nested relation is NOT a *Many
        for relation in query.relations.values():
            if not relation.contains_many(query.relations):
                # Don't use the relation.entity table to get columns, use the join aliased table
                table = self._get_join_table(query, relation.name)
                #dump(table, 'xxx', relation.name)
                columns = relation.entity.selectable_columns(table)
                for column in columns:
                    #x = sa.alias(column, 'x')
                    query.selects.append(column.label(quoted_name(relation.name + '__' + column.name, True)))

        # Build first query
        query, saquery = self._build_query(method, query)
        queries.append({
            'name': 'main',
            'query': query,
            'saquery': saquery,
            'sql': str(saquery),
        })

        # So we have our first query perfect
        # Now we need to build a second or third query for all *Many relations
        relation: Relation
        for relation in query.relations.values():
            #if type(relation) == HasMany or type(relation) == BelongsToMany:
            if relation.is_many():
                # New secondary relation query
                query2 = self.query.copy()

                # Build ORM Relations but force HasMany joins to INNER JOIN
                self._build_orm_relations(query2)

                # Only if Many-To-Many add in the main tables pivot ID
                if type(relation) == BelongsToMany:
                    join_table = self._get_join_table(query2, relation.join_tablename)
                    query2.selects.append(
                        getattr(join_table.c, relation.left_key).label(
                            quoted_name(relation.name + '__' + relation.left_key, True)
                        )
                    )

                # Set selects to only those in the related table
                table = self._get_join_table(query2, relation.name)
                columns = relation.entity.selectable_columns(table)
                for column in columns:
                    query2.selects.append(column.label(quoted_name(relation.name + '__' + column.name, True)))

                # Add in selects for any *One sub_relations
                for sub_relation in query2.relations.values():
                    if relation.name + '__' not in sub_relation.name: continue
                    if sub_relation.contains_many(query2.relations, skip=relation.name.split('__')): continue
                    table = self._get_join_table(query2, sub_relation.name)
                    columns = sub_relation.entity.selectable_columns(table)
                    for column in columns:
                        query2.selects.append(column.label(quoted_name(sub_relation.name + '__' + column.name, True)))

                # Add .filter() as .where()
                query2.wheres.extend(query2.filters)

                # Add where to show only joined record that were found
                # Cant use INNER JOIN instead because it would limit further sub many-to-many
                query2.wheres.append((relation.name + '.' + relation.entity.pk, '!=', None))

                # Swap .sort() to .order_by
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

    async def _getXXX(self) -> List[E]:

        # Multi query notes
        # Build a self.queries DICT and add each
        # Then execute all and combine.  Why? So .sql() can dump it
        # queries = {
        #   'main': 'actual main sql',
        #   'posts': 'secondary posts query'
        # }

        # Query Optimization
        # On the PRIMARY query, if there are no WHERE or ORDER BY on a HasMany relation
        # then you can remove those HasMany from the JOIN, they are not used

        # On the SECONDARY queries, if there are no WHERE or ORDER BY on HasOne relations
        # then you can remove those HasOne from the JOIN, they are not used

        # Here is a perfect example of a 3 query that could be optimized
        # In [17]: dump((await User.query()
        #     ...:     .include('info', 'contact', 'posts.comments')
        #     ...:     .get()
        #     ...: )[1])

        # Here, the HasMany joins can be removed since there is no where or order_by
        # So remove POSTS and COMMENTS
        # MAIN QUERY
        # SELECT DISTINCT auth_users.id, auth_users.email, auth_users.app1_extra, auth_user_info.id AS "info__id", auth_user_info.extra1 AS "info__extra1", auth_user_info.user_id AS "info__user_id", contacts.id AS "contact__id", contacts.name AS "contact__name", contacts.title AS "contact__title", contacts.address AS "contact__address", contacts.phone AS "contact__phone", contacts.user_id AS "contact__user_id"
        # FROM auth_users LEFT OUTER JOIN auth_user_info ON auth_users.id = auth_user_info.user_id LEFT OUTER JOIN contacts ON auth_users.id = contacts.user_id LEFT OUTER JOIN posts ON auth_users.id = posts.creator_id LEFT OUTER JOIN comments ON posts.id = comments.post_id

        # Here the HasOne of UserInfo and UserContact can be removed
        # Technically the HasMany comments can also be removed, but not sure how to determine that
        # SECONDARY QUERY
        # SELECT DISTINCT posts.id AS "posts__id", posts.unique_slug AS "posts__unique_slug", posts.title AS "posts__title", posts.other AS "posts__other", posts.creator_id AS "posts__creator_id"
        # FROM auth_users LEFT OUTER JOIN auth_user_info ON auth_users.id = auth_user_info.user_id LEFT OUTER JOIN contacts ON auth_users.id = contacts.user_id LEFT OUTER JOIN posts ON auth_users.id = posts.creator_id LEFT OUTER JOIN comments ON posts.id = comments.post_id
        # WHERE posts.id IS NOT NULL

        # Here the HasOne of UserInfo and UserContact can be removed
        # Here the HasMany Posts obviously can NOT be removed since comments relys on posts
        # SECONDARY QUERY
        # SELECT DISTINCT comments.id AS "posts__comments__id", comments.title AS "posts__comments__title", comments.body AS "posts__comments__body", comments.post_id AS "posts__comments__post_id"
        # FROM auth_users LEFT OUTER JOIN auth_user_info ON auth_users.id = auth_user_info.user_id LEFT OUTER JOIN contacts ON auth_users.id = contacts.user_id LEFT OUTER JOIN posts ON auth_users.id = posts.creator_id LEFT OUTER JOIN comments ON posts.id = comments.post_id
        # WHERE comments.id IS NOT NULL



        # Build query
        # Query builder does not look at self variables, it is stand alone
        # because I use it multiple times for relations each with slightly
        # different query parts.  Thus the .copy()

        # First query
        query = self.query.copy()
        self._build_orm_relations(query)

        # Add all selects where NOT HasMany
        query.selects = self.entity.selectable_columns()
        for relation in query.relations.values():
            if type(relation) == HasOne or type(relation) == BelongsTo:
                columns = relation.entity.selectable_columns()
                for column in columns:
                    query.selects.append(column.label(quoted_name(relation.name + '__' + column.name, True)))

        # Build first query
        query, saquery = self._build_query('select', query)
        #dump(query)
        #print("MAIN QUERY")
        #print(saquery)

        # Execute first query
        results = await self.entity.fetchall(saquery)
        #print(saquery)

        def results2dict(results):
            l = []
            for result in results:
                d = {}
                for column in result.keys():
                    d[str(column)] = getattr(result, column)
                l.append(d)
            return l

        #dump('RESULTS', results)
        #dump('RESULTS-2-DICT', results2dict(results))

        # So we have our first query perfect
        # Now we need to build a second or third query for all has_many
        has_many = {}
        for relation in query.relations.values():
            if type(relation) == HasMany:
                # New secondary relation query
                query2 = self.query.copy()

                # Build ORM Relations but force HasMany joins to INNER JOIN
                self._build_orm_relations(query2)

                # Set selects to primary table ID + relation column
                #if '__' in relation.name:
                #    dump(relation.name)
                #    query2.selects = ['posts__id']
                #else:
                #    query2.selects = [relation.entity.pk]
                for column in relation.entity.selectable_columns():
                    query2.selects.append(column.label(quoted_name(relation.name + '__' + column.name, True)))
                #query2.selects.extend(relation.entity.selectable_columns())

                # Add .filter() as .where()
                query2.wheres.extend(query2.filters)

                # Add where to show only joined record that were found
                # Don't use innerjoin xxxxxxxxxxxxxxxxxxxxxxx
                query2.wheres.append((relation.name + '.' + relation.entity.pk, '!=', None))

                # Swap .sort() to .order_by
                query2.order_by = query2.sort

                # Build secondary relation query
                query2, saquery2 = self._build_query('select', query2)
                print(); print("SECONDARY QUERY");
                print(saquery2)

                # Execute secondary relation query
                results2 = await self.entity.fetchall(saquery2)
                #print(saquery2)
                #dump("SECOND RESULTS", results2)
                #dump(results2[0].keys())

                # Add secondary results to has_many Dictionary for _build_orm_results
                has_many[relation.name] = results2

        # Convert results to List of entities
        entities = self._build_orm_results(query, results, has_many)

        # Return List of Entities
        #dump('ENTITIES', entities)
        return entities

    def _build_queryXX(self, method: str, query: Query) -> Tuple:

        # Before we call the parent Builder we need to build our ORM relations,
        # translate those into regular .join() and derive our .select() columns.

        # Build ORM relations from .include() and add append to query.joins
        #self._build_orm_relations(query)

        #dump(query)


        # NO!! Because if select is blank the base Builder adds ALL fields with proper alias based on JOIN!!!
        # But I do need to pass in custom selects on multi-select many-to-many

        # # Build selects for main table
        # # Only add selects if selects is EMPTY.  Why?  If its not empty, I have overwridden
        # # the selects for many-to-many multi-query porposes
        # if not query.selects:
        #     # Remember the base Builder accepts string OR actual SQLAlchemy columns as selects!
        #     query.selects.extend(self.entity.selectable_columns())

        #     # Build relation selects
        #     for relation in query.relations.values():

        #         if type(relation) == HasOne or type(relation) == BelongsTo:
        #             #columns = relation.entity.selectable_columns()
        #             query.selects.extend(relation.entity.selectable_columns())
        #             #for column in columns:
        #             #    selects.append(column.label(quoted_name(relation.name + '.' + column.name, True)))

        #dump(query)

        # Call Parent _build_query()
        return super()._build_query(method, query)

    def _build_selectXX(self, query: Query):
        # Get models selectable columns
        # Infer from model, not all columns in table as model may have less columns
        selects = self.entity.selectable_columns()

        # Add in relations selectable columns
        if query.relations:
            for relation in query.relations.values():
                if type(relation) == HasOne or type(relation) == BelongsTo or 1 == 1:
                    columns = relation.entity.selectable_columns()
                    for column in columns:
                        selects.append(column.label(quoted_name(relation.name + '.' + column.name, True)))

        # Start basic select with all selectable columns
        # We use .distinct() because of joins for wheres but not for selects
        saquery = sa.select(selects).distinct()
        if query.joins is not None:
            saquery = saquery.select_from(query.joins)

            #<sqlalchemy.sql.selectable.Join at 0x7f3bba4d6b80; Join object on Join object on posts(139894517854416) and auth_users(139894518106720)(139894505433792) and comments(139894517857968)>

        return saquery

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

        relations: OrderedDict[str, Relation] = ODict()
        for include in query.includes:
            parts = [include]
            if '.' in include: parts = include.split('.')

            entity = self.entity
            parts_added = []
            for part in parts:
                field = entity.modelfields.get(part)
                if not field: continue
                if field.column is not None: continue

                parts_added.append(part)
                relation_name = '__'.join(parts_added)

                # If any relation found
                if field.relation:  #if relation_tuple:
                    # Get relation model class from IoC or dynamic Imports
                    relation: Relation = field.relation.fill(field)

                    # Set a new name based on relation_name dot notation for nested relations
                    relation.name = relation_name

                    # Add relation to List only once
                    if relation_name not in relations:
                        # We have to deepcopy a relationship becuase if we have owner and creator
                        # and both of those user models have a "Contact" model, that contact model is a
                        # single instance.  We want separate instances of each relationship
                        relations[relation_name] = deepcopy(relation)

                        # Many-To-Many
                        if type(relation) == BelongsToMany:
                            # We have to join 2 tables in a many-to-many
                            # First the relation table (sometimes called intermediate or pivot table)
                            # Second the actual related table
                            # No need to alias *Many joins like we do *One joins because it will never be done twice

                            # Join the main table with the relation/intermediate/pivot table
                            #main_tablename = '__'.join(relation_name.split('__')[0:-1])
                            #dump(main_tablename) # post
                            #main_table = self._get_join_table(query, entity.table.name)
                            #dump(query.joins) # singular post
                            #dump(entity.table.name) #plural posts
                            #dump(relation.name) # post__tags
                            #dump(main_table)

                            alias=relation_name
                            main_table = entity.table
                            pivot_join_table = sa.alias(relation.join_table) # Notice no name=alias, just let it append _1, _2... for pivot

                            # If we are joining sub tables, the main_table will be an alias as well
                            if entity != self.entity:
                                # Get the table from the join based on all but last part of relation_name
                                main_tablename = '__'.join(relation_name.split('__')[0:-1])
                                main_table = self._get_join_table(query, main_tablename)

                            #left = self._column(getattr(entity.table.c, entity.pk))
                            #right = self._column(getattr(relation.join_table.c, relation.left_key))

                            left = self._column(getattr(main_table.c, entity.pk))
                            right = self._column(getattr(pivot_join_table.c, relation.left_key))
                            join = Join(
                                #table=relation.join_table,
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

                            join_table = relation.entity.table
                            if join_table.name != alias:
                                join_table = sa.alias(relation.entity.table, name=alias)
                            #left = self._column(getattr(relation.join_table.c, relation.right_key))
                            #right = self._column(getattr(relation.entity.table.c, relation.entity.pk))

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
                        #elif type(relation) == BelongsTo or type(relation) == HasOne or type(relation) == HasMany:
                        #elif relation.is_one():
                            # These One-To-One or One-To-Many on the BelongsTo side can be joined
                            # Multiple times.  For exampel post creator and post owner both join User table
                            # So they require aliases

                            # Alias the Joined Table (so we can join the same table multiple times if needed, like owner and creator)
                            alias=relation_name
                            main_table = entity.table
                            join_table = relation.entity.table
                            #dump("alias: " + alias + " - relation.entity.table.name: " + join_table.name)
                            if join_table.name != alias:
                                join_table = sa.alias(relation.entity.table, name=alias)

                            # If we are joining sub tables, the main_table will be an alias as well
                            if entity != self.entity:
                                # Get the table from the join based on all but last part of relation_name
                                main_tablename = '__'.join(relation_name.split('__')[0:-1])
                                main_table = self._get_join_table(query, main_tablename)

                            # Join condition columns
                            left = self._column(getattr(main_table.c, relation.local_key))
                            right = self._column(getattr(join_table.c, relation.foreign_key))

                            # Append new Join
                            join = Join(
                                table=join_table,
                                tablename=str(join_table.name),
                                left=left,
                                right=right,
                                onclause=left.sacol == right.sacol,
                                alias=alias,
                                method='outerjoin'
                            )
                            query.joins.append(join)

                            #dump(join)

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

                # Swap entities for next loop
                entity = relation.entity

        # Set query.relations
        query.relations = relations

    def _build_orm_results(self, query: Query, primary: List, secondary: Dict = {}) -> List[E]:
        # No primary results, return empty List
        if not primary: return []

        log.nl().header('Relations')
        dump(query.relations)

        log.nl().header('Primary Results')
        dump(primary)

        log.nl().header('Has Many Data')
        dump(secondary)

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
            log.nl().header('Filling *One Relations for ' + rel_name)

            # Determin if data is primary or secondary
            primary = (rel_name == 'primary')

            # Split rel_name into __ parts
            rel_name_parts = rel_name.split('__')

            # Get the actual field, relation and entity for this relation rel_name
            entity = self.entity
            if not primary:
                for rnpart in rel_name_parts:
                    field: Field = entity.modelfields.get(rnpart)
                    entity = field.relation.fill(field).entity

            #log.item('Field: ' + str(field))
            log.item('Entity: ' + str(entity))
            log.item('Data Keys: ' + str(data[0].keys()))

            # Add a new List to our Dict of models
            models[rel_name] = {}

            # Pk field and column
            pk = entity.pk
            pk_column = entity.mapper(pk).column()
            if not primary: pk_column = rel_name + '__' + pk_column

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
                else:
                    root_model = entity.mapper(row, rel_name).model()

                # Get pk value
                pk_value = getattr(root_model, pk)

                # Track completed relations so I can remove from our relations list later
                completed_relations = []

                # Loop only *One relations that apply to this one "data" model
                relation: Relation
                for relation in relations.values():

                    # Only look at relations that begin with this relation__ and are *One
                    if not primary and rel_name + '__' not in relation.name: continue

                    # Walk up relations and exclude if ANY relation is a *Many starting from rel_name and up
                    if relation.contains_many(query.relations, skip=rel_name_parts): continue

                    # Log output
                    if i == 0: log.item('Relation: ' + relation.name + ' - ' + str(relation))

                    # RowProxy results lookup prefix
                    prefix = relation.name

                    # Get all relation fieldnames from relation.name split
                    fieldnames = relation.name.split('__')
                    if not primary:
                        # Skip the first __ parts of rel_name
                        fieldnames = fieldnames[len(rel_name_parts):]
                    if i == 0: log.item2('  Fieldnames: ' + ', '.join(fieldnames))

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
                    if i == 0: log.item2('  Model Field: ' + fieldname)
                    if i == 0: log.item2('  Field Model: ' + str(model.__class__))

                    # Convert this one rows relation data into a sub_relation model
                    # Only convert each unique *One record just once, or else pull from singles cache
                    # The odd part about this cache is if you include many nested relations one one parent model
                    # And a child model also uses the same child, it too will include all nested relations
                    # Example if you do .include('creator.info', 'owner').  If owner is id=1 and id=1 was already
                    # a creator, that owner will also have the nested INFO filled out, because it pulls from the cache.
                    if relation.entity.tablename not in singles: singles[relation.entity.tablename] = {}
                    sub_model_pk = relation.name + '__' + relation.entity.mapper(entity.pk).column()
                    sub_model_pk_value = getattr(row, sub_model_pk)
                    if sub_model_pk_value not in singles[relation.entity.tablename]:
                        singles[relation.entity.tablename][sub_model_pk_value] = relation.entity.mapper(row, prefix).model()

                    # Get sub_model from singles cache
                    sub_model = singles[relation.entity.tablename][sub_model_pk_value]
                    #sub_model = relation.entity.mapper(row, prefix).model() # No cache version

                    # Add this converted sub_model to the walked down parent model
                    setattr(model, fieldname, sub_model)

                    # Mark relation as complete so I can delete from relations Dict later
                    completed_relations.append(relation.name)

                # All *One relations have been converted and merged
                # Add this fully converted (including nested *One relations) model to List of models
                models[rel_name][pk_value] = root_model
                i += 1

            # Delete all completed relations from our relation deepcopy.  We will not need them again
            for completed_relation in completed_relations:
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
        log.nl().header('Leftover Relations are *Many')
        dump(relations)

        # All records in models Dict are *Many and the main Primary dataset
        # All remaining relations are the *Many which should match the models Dict key
        # Looping the *Many relations in REVERSE gives us the deepest relations first which is critical
        log.nl().header('Combining Recursive *Many Models')
        for relation in reversed(relations.values()):

            # Relation name parts
            relation_parts = relation.name.split('__')
            field = relation_parts[-1]

            # Get parent and child Dict of models
            children_name = relation.name
            children = models[relation.name]
            parents_name = 'primary'
            if len(relation_parts) > 1: parents_name = '__'.join(relation_parts[:-1])
            dump(parents_name)
            if parents_name in models:
                # Parent is a *Many so grab from models
                parents = models[parents_name]
            else:
                # Parent is a *One, so grap from singles cache
                parents = singles[query.relations.get(parents_name).entity.tablename]

            log.item('Combining child: ' + children_name + ' into parent: ' + parents_name)

            # Merge in Many-To-Many by using the original RowProxy result which contains
            # The pivot tables joining column (left_key)
            if type(relation) == BelongsToMany:
                left_key = relation.name + '__' + relation.left_key
                right_key = relation.name + '__' + relation.entity.mapper(relation.entity.pk).column()

                dump(parents, left_key, right_key)

                # Loop raw RowProxy to find proper pivot keys
                for row in secondary[relation.name]:
                    dump(row.keys())
                    left_id = getattr(row, left_key)
                    right_id = getattr(row, right_key)

                    # Set None field to empty List
                    if getattr(parents[left_id], field) is None:
                        setattr(parents[left_id], field, [])

                    # Append to list using deepcopy
                    getattr(parents[left_id], field).append(
                        # We must deep copy the record becuase we dedup the *Many
                        # but they could be used multiple times
                        # ?? Hum maybe not, good if you change one it changes them all
                        # But all the *One will NOT be like this I don't believe, have to test
                        #deepcopy(child[right_id])
                        children[right_id]
                    )

            else:
                # These are One-To-Many on the *Many side which means the id back to parent is in the model itself
                for child in children.values():
                    parent = parents[getattr(child, relation.foreign_key)]
                    field = relation_parts[-1]

                    # Set None field to empty list
                    if getattr(parent, field) is None:
                        setattr(parent, field, [])

                    # Append each *Many model
                    getattr(parent, field).append(child)


        log.nl().header('Singles Cache')
        dump(singles)

        log.nl().header('Secondary *Many Models')
        dump(models)

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

    def _build_orm_resultsXX(self, query: Query, results, has_many: Dict = {}) -> List[E]:
        # No results, return empty List
        if not results: return []

        # Loop each raw SQLAlchemy DB results and convert to Model entities with relations
        entities = []
        for row in results:
            # Convert DB result to model (no relations, just main table)
            model = self.entity.mapper(row).model()
            #dump(model)
            #dump(query.relations)

            # Loop each relation and merge in results
            for relation in query.relations.values():
                relation_name = relation.name
                prefix = relation_name
                current_model = model

                if type(relation) == BelongsToMany:
                    pk = prefix + '__' + relation.left_key
                else:
                    pk = prefix + '__' + relation.foreign_key

                # Get nested model based on dotnotation
                if '__' in relation.name:
                    parts = relation.name.split('__')
                    #relation_name = parts[-1]
                    for i in range(0, len(parts) - 1):
                        current_model = getattr(current_model, parts[i])

                # Some models are single, some are multiple, normalize all to List
                if type(current_model) != list: current_model = [current_model]

                # Merge in single relations
                if type(relation) == HasOne or type(relation) == BelongsTo:
                    for related_model in current_model:
                        related_data = relation.entity.mapper(row, prefix).model()
                        rn = relation_name.split('__')[-1]
                        #setattr(related_model, relation_name, related_data)
                        setattr(related_model, rn, related_data)

                # Merge in multiple relations from secondary query results saved to has_many Dictionary
                elif type(relation) == HasMany or type(relation) == BelongsToMany and relation.name in has_many:
                    for related_model in current_model:
                        related_entities = []
                        for related_row in has_many[relation.name]:
                            if getattr(related_row, pk) == getattr(related_model, related_model.__class__.pk):
                                related_entity = relation.entity.mapper(related_row, prefix).model()
                                #dump(related_entity)
                                related_entities.append(related_entity)
                        setattr(related_model, relation_name, related_entities)

            # Add complete model to list of entities
            entities.append(model)

        # Return List of Entities
        return entities

    def _connection(self):
        return self.entity.connection

    def _pk(self):
        return self.entity.pk

    def _column_from_string(self, dotname: str, query: Query) -> Tuple:
        if '.' in dotname:
            parts = dotname.split('.')
            relation = query.relations.get('.'.join(parts[:-1]))
            table = self._get_join_table(query, relation.name)  # Get table from join alias since its a relation
            field = parts[-1]
            name = self.entity.mapper(field).column()
        else:
            name = self.entity.mapper(dotname).column()
            table = query.table

        tablename = str(table.name)
        column = table.columns.get(name)
        return (table, tablename, column, name, self._connection())

    def _get_join_table(self, query: Query, tablename: str):
        """Get the join table for this tablename"""
        # Get table from joins by tablename
        for join in query.joins:
            if join.tablename == tablename:
                return join.table

        # Not found by name, check alias
        for join in query.joins:
            if join.alias == tablename:
                #dump(tablename)
                #dump(join)
                return join.table


# IoC Class Instance
_OrmQueryBuilderIoc: _OrmQueryBuilder = uvicore.ioc.make('OrmQueryBuilder', _OrmQueryBuilder)

# Actual Usable Model Class Derived from IoC Inheritence
class OrmQueryBuilder(Generic[B, E], _OrmQueryBuilderIoc[B, E], BuilderInterface[B, E]):
    pass
