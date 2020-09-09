import operator as operators
from typing import (Any, AsyncGenerator, Dict, List, Mapping, Optional, Tuple, Union)

import sqlalchemy as sa
from sqlalchemy.sql import ClauseElement

import uvicore
from uvicore import db
from uvicore.contracts import Model as ModelInterface
from uvicore.support.dumper import dd, dump
from uvicore.support.pydantic import BaseModel

from .metaclass import ModelMetaclass


class QueryBuilder:

    def __init__(self, entity = None):
        self.entity = entity
        self.conn = entity.__connection__
        self.table = entity.__table__
        self._where = []
        self._where_or = []

    # def __get__(self, instance, owner):
    #     return self.__class__(owner)

    def where(self, column: Union[str, List[Tuple]], operator: str = None, value: Any = None):
        if type(column) == str:
            if not value:
                value = operator
                operator = '='
            self._where.append((column, operator.lower(), value))
        else:
            for where in column:
                if len(where) == 2:
                    self.where(where[0], '=', where[1])
                else:
                    self.where(where[0], where[1], where[2])
        return self

    def or_where(self, wheres: List[Tuple]):
        # if not value:
        #     value = operator
        #     operator = '='
        #self._where_or.append((column, operator, value))
        where_or = []
        for where in wheres:
            if len(where) == 2:
                where_or.append((where[0], '=', where[1]))
            else:
                where_or.append((where[0], where[1].lower(), where[2]))
        self._where_or = where_or
        return self

    async def find(self, pk_value: Any):
        primary = self._primary()
        self.where(primary, pk_value)
        table, query = self._build('select')
        results = await self.entity._fetchone(query)
        if results:
            return self.entity._to_model(results)

    async def get(self):
        # Build query
        table, query = self._build('select')
        print(query)

        # Execute query
        results = await self.entity._fetchall(query)

        # Convert results to List of entity
        models = []
        for row in results:
            models.append(self.entity._to_model(row))

        # Clear builder
        #entity.__query__ = {}

        # Return List of entity
        return models

    # async def insert(self, values: List):
    #     # Convert each entity into a dictionary of table data
    #     bulk = []
    #     for value in values:
    #         bulk.append(value._to_table())
    #     query = self.table.insert()
    #     await self.entity._execute(query, bulk)

    def _build(self, method: str = 'select'):
        table = self.table
        query = None

        # where
        #   select
        #   update (not in insert)
        #   delete

        if method == 'select':
            # if self._select:
            #     columns = []
            #     #for select in self._select:
            #     columns = [getattr(table.c, x) for x in self._select]
            #     query = sa.select(columns)
            # else:
            query = sa.select([table])

        # Where And
        if self._where:
            where_ands = self._build_where(self._where)
            query = query.where(sa.and_(*where_ands))

        # Where Or
        if self._where_or:
            where_ors = self._build_where(self._where_or)
            query = query.where(sa.or_(*where_ors))


        return table, query

    def _build_where(self, wheres: List[Tuple]):
        statements = []
        table = self.table
        for where in wheres:
            column, operator, value = where
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

    def _primary(self):
        for field in self.entity.__fields__.values():
            extra = field.field_info.extra
            if 'primary' in extra and extra.get('primary') == True:
                return field.name



class _Model(ModelInterface, BaseModel, metaclass=ModelMetaclass):
    """Uvicore ORM Base Model.

    NOTE: I hacked pydantic to allow shadowing of BaseModel.  This means you
    can have fields (columns) called `get`, or `find`, `where` etc... and pydantic
    won't complain even though `get/find/where` are classmethods.  You cannot however
    have fields of `save` or `delete` since those are instance methods.
    """

    # class query(Query):
    #     pass

    #_query = Query()

    # @classmethod
    # def query(entity):
    #     return QueryBuilder(entity)

    # Example of my shadow methods working now!
    # @classmethod
    # def email(entity):
    #     return 'email classmethod here'

    @classmethod
    async def get(entity):
        return await QueryBuilder(entity).get()

    @classmethod
    async def find(entity, id: Any):
        return await QueryBuilder(entity).find(id)

    @classmethod
    def where(entity, column: Union[str, List[Tuple]], operator: str = None, value: Any = None):
        return QueryBuilder(entity).where(column, operator, value)

    @classmethod
    #def where_or(entity, column: str, operator: str = None, value: Any = None):
    def or_where(entity, wheres: List):
        return QueryBuilder(entity).or_where(wheres)

    # @classmethod
    # async def insert(entity, values: List):
    #     return await QueryBuilder(entity).insert(values)

    # @classmethod
    # def email(entity):
    #     return 'asdf'

    def __init__(self, **data: Any) -> None:
        # Call pydantic parent
        super().__init__(**data)

        # Fill in callback properties
        for (key, callback) in self.__callbacks__.items():
            setattr(self, key, callback(self))

    def __getattribute__(self, name):
        # __getattribute__ intercepts ALL attribute accessors
        # while __getattr__ intercepts non existing attribute accessors
        # This is where we intercept and handle lazy loaded relations
        if name == 'creator':
            return 'creator here'
        else:
            # Must return the parents __getattribute__ or we get infinite recursion
            return BaseModel.__getattribute__(self, name)

    @classmethod
    def _info(entity, detailed: bool = False):
        fields = {}
        for (key, field) in entity.__fields__.items():
            info = field.field_info
            extra = info.extra
            fields[key] = {
                #'name': field.name,
                'column': extra.get('column'),
                'default': info.default,
                'required': info.required,
                'callback': extra.get('callback'),
                'title': info.title,
                'description': info.description,
                'read_only': extra.get('readOnly'),
                'write_only': extra.get('writeOnly'),
                'properties': extra.get('properties'),
                #'field_info': info,
                #'extra': extra,
            }
            if detailed:
                fields[key]['class_dict'] = entity.__dict__
                fields[key]['field_info'] = info,
                fields[key]['extra'] = extra,

        return {
            'connection': db.connection(entity.__connection__),
            'tablename': entity.__tablename__,
            'table': entity.__table__,
            'fields': fields,
        }

    # @classmethod
    # def where(entity, column: str, operator: str, value: Any = None):
    #     if not value:
    #         value = operator
    #         operator = '='

    #     if 'where' not in entity.__query__: entity.__query__['where'] = []
    #     entity.__query__['where'].append({'column': column, 'operator': operator, 'value': value})
    #     return entity

    # @classmethod
    # def include(entity, *args):
    #     entity.__query__['include'] = list(args)
    #     return entity

    # @classmethod
    # async def find(entity, id: Any):
    #     # Build query
    #     table = entity.__table__
    #     query = table.select().where(table.c.id == id)
    #     results = await entity._fetchone(query)
    #     if results:
    #         return entity._to_model(results)

    # @classmethod
    # async def all(entity):
    #     table = entity.__table__
    #     query = table.select()
    #     results = await entity._fetchall(query)
    #     models = []
    #     for row in results:
    #         # Convert table result row into entity model
    #         models.append(entity._to_model(row))
    #     return models

    # @classmethod
    # async def db(entity):
    #     return await uvicore.db.database(entity.__connection__)

    # @classmethod
    # async def get(entity):
    #     # Build query
    #     table, query = entity._build_query('select')

    #     # Execute query
    #     results = await entity._fetchall(query)

    #     # Convert results to List of entity
    #     models = []
    #     for row in results:
    #         models.append(entity._to_model(row))

    #     # Clear builder
    #     entity.__query__ = {}

    #     # Return List of entity
    #     return models

    # @classmethod
    # def _build_query(entity, method: str = 'select'):
    #     table = entity.__table__
    #     qb = entity.__query__
    #     query = None

    #     if method == 'select':
    #         query = sa.select()

    #     return table, query

    # @classmethod
    # async def getOLD(entity):
    #     fields = entity.__fields__
    #     qb = entity.__query__
    #     table = entity.__table__
    #     selects = [table]
    #     joins = []

    #     # Add include
    #     if 'include' in qb:
    #         #>>> print(users.join(addresses))
    #         #users JOIN addresses ON users.id = addresses.user_id

    #         includes = qb['include']
    #         for include in qb['include']:
    #             field = fields.get(include)
    #             if not field: continue
    #             extra = field.field_info.extra

    #             # Ignore include if its an actual column
    #             if extra.get('column') is not None: continue

    #             # Handle one-to-one or many-to-one relations
    #             if 'has_one' in extra:
    #                 has_one = extra['has_one']
    #                 rel_model = None
    #                 rel_foreign_key = 'id'
    #                 rel_local_key = field.name + '_id'
    #                 if type(has_one) == tuple:
    #                     rel_model = has_one[0]
    #                     if len(has_one) >= 2:
    #                         rel_foreign_key = has_one[1]
    #                     if len(has_one) == 3:
    #                         rel_local_key = has_one[2]
    #                 else:
    #                     rel_model = has_one

    #                 # Get relations table
    #                 rel_table = rel_model.__table__
    #                 #dd(rel_model, rel_table, rel_foreign_key, rel_local_key)

    #                 # Add a join
    #                 join = sa.join(
    #                     left=table,
    #                     right=rel_table,
    #                     onclause=getattr(table.c, rel_local_key) == getattr(rel_table.c, rel_foreign_key)
    #                 )
    #                 joins.append(join)
    #                 selects.append(rel_table)

    #         # query = query.join(
    #         #     auth_users,
    #         #     table.c.creator_id == auth_users.c.id
    #         # )

    #         # j = join(user_table, address_table,
    #         #         user_table.c.id == address_table.c.user_id)
    #         # stmt = select([user_table]).select_from(j)

    #         #>>> print(users.join(addresses,
    #         #addresses.c.email_address.like(users.c.name + '%'))

    #     #query = table.select().select_from(j)
    #     #query = sa.select([table, auth_users]).select_from(j)
    #     #query = sa.select([table])
    #     if joins:
    #         #query = sa.select(selects).select_from(*joins)
    #         query = sa.select([
    #             table.c.id,
    #             table.c.unique_slug,
    #             table.c.title,

    #             rel_table.c.id.label('creator.id'),
    #             rel_table.c.email.label('creator.email')
    #         ]).select_from(*joins)
    #     else:
    #         query = sa.select(selects)

    #     # Add where
    #     if 'where' in entity.__query__:
    #         for where in entity.__query__['where']:
    #             query = query.where(getattr(table.c, where['column']) == where['value'])

    #     # query = session.query(Domain.domain_name, Subdomain.subdomain_name, Title.title, Title.status, Title.response_len, Title.created_on, Title.updated_on)
    #     # query = query.join(Title).join(Subdomain)

    #     #print(query)

    #     results = await entity._fetchall(query)
    #     # for row in results:
    #     #     dd(row.items())

    #     # dd(results)

    #     models = []
    #     for row in results:
    #         models.append(entity._to_model(row))

    #     # Clear builder
    #     entity.__query__ = {}
    #     return models

    @classmethod
    async def insert(entity, values: List):
        """Insert an array of models in bulk"""
        # Convert each entity into a dictionary of table data
        bulk = []
        for value in values:
            bulk.append(value._to_table())
        table = entity.__table__
        query = table.insert()
        await entity._execute(query, bulk)

    @classmethod
    async def _execute(entity, query: Union[ClauseElement, str], values: Union[List, Dict] = None) -> Any:
        return await db.execute(query=query, values=values, connection=entity.__connection__)

    @classmethod
    async def _fetchone(entity, query: Union[ClauseElement, str], values: Dict = None) -> Optional[Mapping]:
        return await db.fetchone(query=query, connection=entity.__connection__)

    @classmethod
    async def _fetchall(entity, query: Union[ClauseElement, str], values: Dict = None) -> List[Mapping]:
        return await db.fetchall(query=query, connection=entity.__connection__)

    @classmethod
    def _to_model(entity, row):
        """Convert a row of table data into a model"""
        model_columns = {}
        for (field_name, field) in entity.__fields__.items():
            column_name = field.field_info.extra.get('column')
            if column_name is not None:
                model_columns[field_name] = getattr(row, column_name)
        return entity(**model_columns)

    async def save(self):
        table = self.__table__
        values = self._to_table()
        query = table.insert().values(**values)
        await self._execute(query)

    async def delete(self):
        pass

    def _to_table(self) -> Dict:
        """Convert an model entry into a dictionary matching the tables columns"""
        table_columns = {}
        for (key, value) in self.__dict__.items():
            field = self.__class__.__fields__.get(key)
            extra = field.field_info.extra
            column_name = extra.get('column')
            if column_name and not extra.get('readOnly'):
                table_columns[column_name] = value
        return table_columns


# IoC Class Instance
Model: ModelInterface = uvicore.ioc.make('Model')

# Public API for import * and doc gens
__all__ = ['_Model', 'Model']
