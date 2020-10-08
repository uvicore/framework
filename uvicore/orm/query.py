from __future__ import annotations

import operator as operators
from copy import copy
from typing import Any, Dict, Generic, List, Tuple, TypeVar, Union

import sqlalchemy as sa
from pydantic.utils import Representation

import uvicore
from uvicore.database.builder import Column, Join, Query, QueryBuilder
from uvicore.orm.fields import BelongsTo, Field, HasMany, HasOne, Relation
from uvicore.support.dumper import dd, dump

E = TypeVar('E')

class _OrmQueryBuilder(Generic[E], QueryBuilder[E]):
    """ORM Query Builder"""

    def __init__(self, entity: E):
        self.entity = entity
        super().__init__()
        self.query.table = entity.table
        #self.query.joins = None

    @property
    def _connection(self):
        return self.entity.connection

    def filter(self, column: Union[str, List[Tuple]], operator: str = None, value: Any = None) -> QueryBuilder[E]:
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

    def include(self, *args) -> QueryBuilder[E]:
        # import inspect
        # x = inspect.currentframe()
        # y = inspect.getouterframes(x, 1)
        # context = y[1].code_context
        # #dump(context)
        #args = ['creator.contact']
        for include in args:
            self.query.includes.append(include)
        return self

    def key_by(self, field: str) -> QueryBuilder[E]:
        self.query.keyed_by = field
        return self

    async def link(self, relation: str, values: List) -> None:
        dump('hiii')

    async def find(self, pk_value: Any) -> E:
        # Where on Primary Key
        self.where(self._pk(), pk_value)

        # Build query
        query, saquery = self._build_query('select', copy(self.query))
        #print(saquery)

        # Execute query (yes fetchall not fetchone)
        results = await self.entity.fetchall(saquery)
        #dump('RESULTS', results)

        # Convert results to List of entities
        entities = self._build_orm_results(query, results, multiple=False)

        # Return List of entities
        #dump('ENTITIES', entities)
        return entities

        # if results:
        #     return self.entity.to_model(results)

    async def get(self) -> Union[List[E], Dict[str, E]]:
        # Build query
        # Query builder does not look at self variables, it is stand alone
        # because I use it multiple times for relations each with slightly
        # different query parts
        query, saquery = self._build_query('select', copy(self.query))
        #print(saquery)  # Actual SQL

        # Execute query
        results = await self.entity.fetchall(saquery)

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

        # Convert results to List of entities
        entities = self._build_orm_results(query, results)

        # # So we have our first query perfect
        # # Now we need to build a second or third query for all has_many
        # for relation in self.relations.values():
        #     if type(relation) == HasMany:
        #         dump('hi')
        #         # {
        #         #     'name': 'comments',
        #         #     'type': 'has_many',
        #         #     'field': Field(name='comments', primary=False, description='Post Comments Model', required=False, sortable=False, searchable=False, read_only=False, write_only=False, has_many=('app1.models.comment.Comment', 'post_id', 'id')),
        #         #     'entity': app1.models.comment.CommentModel,  # class
        #         #     'foreign': 'post_id',
        #         #     'local': 'id'
        #         # }

        #         # First Query Remove
        #         # any order_by with a comments. is removed
        #         # any .filter() are removed

        #         # Second Query
        #         # any filters with comments. goto where() on second query
        #         # any order_by with comments. goes here


        #         # Append .filter() into .where()
        #         self.wheres.extend(self.filters)


        #         wheres.append(('one', '=', 'two'))


        #         dump('WHERE', self.wheres)
        #         dump('OR_WHERE', self.or_wheres)
        #         dump('FILTER', self.filters)


        #         table, query = self.build_query('select')
        #         print(query)  # Actual SQL


        #         #re = relation.entity
        #         #x = await re.include('post').where('post.creator_id', 1).get()
        #         #x = await re.include('post').get()


        # Return List of entities
        #dump('ENTITIES', entities)

        # Experimental key_by
        if query.keyed_by:
            keyed_entities = {}
            for entity in entities:
                keyed_entities[getattr(entity, self.keyed_by)] = entity
            return keyed_entities

        # Return List of Entities
        return entities

    def _build_query(self, method: str, query: Query) -> Tuple:

        # Before we call the parent Builder we need to build our ORM relations,
        # translate those into regular .join() and derive our .select() columns.

        # Build ORM relations from .include() and add append to query.joins
        self._build_orm_relations(query)


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
        #             #    selects.append(column.label(sa.sql.quoted_name(relation.name + '.' + column.name, True)))

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
                        selects.append(column.label(sa.sql.quoted_name(relation.name + '.' + column.name, True)))

        # Start basic select with all selectable columns
        # We use .distinct() because of joins for wheres but not for selects
        saquery = sa.select(selects).distinct()
        if query.joins is not None:
            dump('xx', query.joins)
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

        relations: Dict[str, Relation] = {}
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
                relation_name = '.'.join(parts_added)

                # If any relation found
                if field.relation:  #if relation_tuple:
                    # Get relation model class from IoC or dynamic Imports
                    relation: Relation = field.relation.fill(field)

                    # Set a new name based on relation_name dot notation for nested relations
                    relation.name = relation_name

                    # Add relation to List only once
                    if relation_name not in relations:
                        relations[relation_name] = relation

                        # Build Join and add to query
                        left = self._column(getattr(entity.table.c, relation.local_key))
                        right = self._column(getattr(relation.entity.table.c, relation.foreign_key))
                        join = Join(
                            table=relation.entity.table,
                            tablename=str(relation.entity.table.name),
                            left=left,
                            right=right,
                            onclause=left.sacol == right.sacol,
                            alias=relation_name.replace('.', '__'),
                            method='outerjoin'
                        )
                        query.joins.append(join)

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

    def _build_orm_results(self, query: Query, results, multiple: bool = True):
        if not results:
            if multiple: return []
            return None

        entities = []
        for row in results:
            model = self.entity.mapper(row).model()
            for relation in query.relations.values():
                if type(relation) == HasOne or type(relation) == BelongsTo:
                    prefix = relation.name.replace('.', '__')
                    if '.' in relation.name:
                        parts = relation.name.split('.')
                        current_model = model
                        for i in range(0, len(parts) - 1):
                            current_model = getattr(current_model, parts[i])
                        setattr(current_model, parts[-1], relation.entity.mapper(row, prefix).model())
                    else:
                        setattr(model, relation.name, relation.entity.mapper(row, prefix).model())
            entities.append(model)
        if multiple:
            return entities
        else:
            return entities[0]

    def _pk(self):
        return self.entity.pk

    def _column_from_string(self, dotname: str, query: Query) -> Tuple:
        if '.' in dotname:
            parts = dotname.split('.')
            relation = query.relations.get('.'.join(parts[:-1]))
            table = relation.entity.table
            field = parts[-1]
            name = self.entity.mapper(field).column()
        else:
            name = self.entity.mapper(dotname).column()
            table = query.table

        tablename = str(table.name)
        column = table.columns.get(name)
        return (table, tablename, column, name, self._connection)

# IoC Class Instance
_OrmQueryBuilderIoc: _OrmQueryBuilder = uvicore.ioc.make('OrmQueryBuilder', _OrmQueryBuilder)

# Actual Usable Model Class Derived from IoC Inheritence
class OrmQueryBuilder(Generic[E], _OrmQueryBuilderIoc):
    pass
