from __future__ import annotations

import operator as operators
from typing import Any, Dict, Generic, List, Tuple, TypeVar, Union

import sqlalchemy as sa

import uvicore
from uvicore.orm.fields import BelongsTo, Field, HasMany, HasOne, Relation
from uvicore.support import module
from uvicore.support.dumper import dd, dump

E = TypeVar('E')

class QueryBuilder(Generic[E]):

    def __init__(self, entity = None):
        # Entity Info
        self.entity = entity

        # Query Builder
        self.wheres = []
        self.or_wheres = []
        self.includes = []
        self.relations: Dict[str, Relation] = {}
        self.joins = None
        self.keyed_by = None

    @property
    def table(self) -> sa.Table:
        return self.entity.table

    @property
    def modelfields(self) -> Dict[str, Field]:
        return self.entity.modelfields

    def modelfield(self, field) -> Field:
        return self.entity.modelfields.get(field)

    def where(self, column: Union[str, List[Tuple]], operator: str = None, value: Any = None) -> QueryBuilder[E]:
        if type(column) == str:
            if not value:
                value = operator
                operator = '='
            self.wheres.append((column, operator.lower(), value))
        else:
            for where in column:
                if len(where) == 2:
                    self.where(where[0], '=', where[1])
                else:
                    self.where(where[0], where[1], where[2])
        return self

    def or_where(self, wheres: List[Tuple]) -> QueryBuilder[E]:
        # if not value:
        #     value = operator
        #     operator = '='
        #self.or_wheres.append((column, operator, value))
        where_or = []
        for where in wheres:
            if len(where) == 2:
                where_or.append((where[0], '=', where[1]))
            else:
                where_or.append((where[0], where[1].lower(), where[2]))
        self.or_wheres = where_or
        return self

    def include(self, *args) -> QueryBuilder[E]:

        # import inspect
        # x = inspect.currentframe()
        # y = inspect.getouterframes(x, 1)
        # context = y[1].code_context
        # #dump(context)
        #args = ['creator.contact']


        for include in args:
            self.includes.append(include)
        return self

    def key_by(self, field: str):
        self.keyed_by = field
        return self

    async def link(self, relation: str, values: List) -> None:
        dump('hiii')

    async def find(self, pk_value: Any) -> E:
        # Where on Primary Key
        pk = self.entity.pk
        self.where(pk, pk_value)

        # Build query
        table, query = self.build_query('select')
        print(query)

        # Execute query (yes fetchall not fetchone)
        results = await self.entity.fetchall(query)
        dump('RESULTS', results)

        # Convert results to List of entities
        entities = self.build_results(results, multiple=False)

        # Return List of entities
        #dump('ENTITIES', entities)
        return entities

        # if results:
        #     return self.entity.to_model(results)

    #async def get(self) -> Union[List[E], Dict[str, E]]:
    async def get(self) -> List[E]:
        # Build query
        table, query = self.build_query('select')
        print(query)  # Actual SQL

        # Execute query
        results = await self.entity.fetchall(query)

        def results2dict(results):
            l = []
            for result in results:
                d = {}
                for column in result.keys():
                    d[str(column)] = getattr(result, column)
                l.append(d)
            return l

        dump('RESULTS', results)
        #dump('RESULTS-2-DICT', results2dict(results))

        # Convert results to List of entities
        entities = self.build_results(results)

        # So we have our first query perfect
        # Now we need to build a second or third query for all has_many
        for relation in self.relations.values():
            if type(relation) == HasMany:
                # {
                #     'name': 'comments',
                #     'type': 'has_many',
                #     'field': Field(name='comments', primary=False, description='Post Comments Model', required=False, sortable=False, searchable=False, read_only=False, write_only=False, has_many=('app1.models.comment.Comment', 'post_id', 'id')),
                #     'entity': app1.models.comment.CommentModel,  # class
                #     'foreign': 'post_id',
                #     'local': 'id'
                # }



                re = relation.entity
                x = await re.include('post').where('post.creator_id', 1).get()
                #x = await re.include('post').get()


        # Return List of entities
        #dump('ENTITIES', entities)


        # Experimental key_by
        if self.keyed_by:
            keyed_entities = {}
            for entity in entities:
                keyed_entities[getattr(entity, self.keyed_by)] = entity
            return keyed_entities

        # Return List of Entities
        return entities

    def build_results(self, results, multiple: bool = True):
        if not results:
            if multiple: return []
            return None

        entities = []
        for row in results:
            #model = self.entity.to_model(row)
            model = self.entity.mapper(row).model()
            for relation in self.relations.values():
                if type(relation) == HasOne or type(relation) == BelongsTo:
                    relation_name = relation.name
                    if '.' in relation_name:
                        parts = relation_name.split('.')
                        current_model = model
                        for i in range(0, len(parts) - 1):
                            current_model = getattr(current_model, parts[i])
                        #setattr(current_model, parts[-1], relation.entity.to_model(row, relation_name))
                        setattr(current_model, parts[-1], relation.entity.mapper(row, relation_name).model())
                    else:
                        #setattr(model, relation_name, relation.entity.to_model(row, relation_name))
                        setattr(model, relation_name, relation.entity.mapper(row, relation_name).model())
            entities.append(model)
        if multiple:
            return entities
        else:
            return entities[0]

    # async def insert(self, values: List):
    #     # Convert each entity into a dictionary of table data
    #     bulk = []
    #     for value in values:
    #         bulk.append(value.to_table())
    #     query = self.table.insert()
    #     await self.entity._execute(query, bulk)

    def build_query(self, method: str = 'select'):
        table = self.table
        query = None

        # where
        #   select
        #   update (not in insert)
        #   delete

        # insert will never come into this get() or build function

        if method == 'select':
            self.relations = self.build_relations()

            if self.relations: dump('RELATIONS:', self.relations)
            if self.joins is not None: dump('JOINS:', self.joins)

            query = self.build_select()


        # Where And
        if self.wheres:
            where_ands = self.build_where(self.wheres)
            query = query.where(sa.and_(*where_ands))

        # Where Or
        if self.or_wheres:
            where_ors = self.build_where(self.or_wheres)
            query = query.where(sa.or_(*where_ors))


        return table, query

    def build_select(self):
        # Get models selectable columns
        # Infer from model, not all columns in table as model may have less columns
        selects = self.entity.selectable_columns()

        # Add in relations selectable columns
        if self.relations:
            for relation in self.relations.values():
                if type(relation) == HasOne or type(relation) == BelongsTo:
                    columns = relation.entity.selectable_columns()
                    for column in columns:
                        selects.append(column.label(relation.name + '.' + column.name))

        # Start basic select with all selectable columns
        # We use .distinct() because of joins for wheres but not for selects
        query = sa.select(selects).distinct()
        if self.joins is not None:
            query = query.select_from(self.joins)

            #<sqlalchemy.sql.selectable.Join at 0x7f3bba4d6b80; Join object on Join object on posts(139894517854416) and auth_users(139894518106720)(139894505433792) and comments(139894517857968)>

        return query

    def build_relations(self):
        if not self.includes: {}

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
        for include in self.includes:
            parts = [include]
            if '.' in include: parts = include.split('.')

            entity = self.entity
            parts_added = []
            for part in parts:
                field = entity.modelfields.get(part)
                #field = self.modelfield(include)
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

                        # Add joins only for one-to-one or one-to-many inverse
                        # Outer Join in case some foreign keys are nullable
                        #if field.has_one or field.belongs_to:
                        if self.joins is None: self.joins = entity.table
                        self.joins = self.joins.outerjoin(
                            right=relation.entity.table,
                            #onclause=getattr(self.table.c, local) == getattr(entity.table.c, foreign)
                            onclause=getattr(entity.table.c, relation.local_key) == getattr(relation.entity.table.c, relation.foreign_key)
                        )


                        # Contact = uvicore.ioc.make('app1.models.contact.Contact')
                        # self.joins = self.joins.outerjoin(
                        #     right=Contact.table,
                        #     onclause=entity.table.c.id == Contact.table.c.user_id
                        # )

                        # self.joins.append(sa.outerjoin(
                        #     left=self.table,
                        #     right=entity.table,
                        #     onclause=getattr(self.table.c, local) == getattr(entity.table.c, foreign)
                        # ))

                # Swap entities for next loop
                entity = relation.entity

        # Return all relations
        return relations

    def build_where(self, wheres: List[Tuple]):
        statements = []
        #table = self.table
        for where in wheres:
            field, operator, value = where

            # Where on relation
            if '.' in field:
                #relation = self.relations.get(field.split('.')[0])
                #table = relation['entity'].table
                #field = field.split('.')[1]
                #relation = self.relations.get(field.split('.')[0:-1])
                relation = self.relations.get('.'.join(field.split('.')[:-1]))
                table = relation.entity.table
                field = field.split('.')[-1]
            else:
                table = self.table

            # Translate model column into table column
            column = self.entity.mapper(field).column()

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
                op = self.operator(operator)
                statements.append(op(getattr(table.c, column), value))
        return statements

    def operator(self, operator: str):
        ops = {
            '=': operators.eq,
            '==': operators.eq,
            '!=': operators.ne,
            '>': operators.gt,
            '<': operators.lt,
        }
        return ops[operator]
