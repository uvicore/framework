import uvicore
from uvicore import db
from typing import List, Dict, Any, Union
from pydantic import BaseModel
from .metaclass import ModelMetaclass
from uvicore.support.dumper import dump, dd
from uvicore.contracts import Model as ModelInterface
import sqlalchemy as sa

class _Model(ModelInterface, BaseModel, metaclass=ModelMetaclass):

    def __init__(self, **data: Any) -> None:
        # Call pydantic parent
        super().__init__(**data)

        # Fill in callback properties
        for (key, callback) in self.__callbacks__.items():
            setattr(self, key, callback(self))

    @classmethod
    def info(entity, detailed: bool = False):
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
            'connection': entity.__connection__,
            'tablename': entity.__tablename__,
            'table': entity.__table__,
            'fields': fields,
        }

    @classmethod
    def find(entity, id: Any):
        table = entity.__table__
        query = table.select().where(table.c.post_id == id)
        results = db.fetchone(entity, query)
        if results:
            return entity._to_model(results)

    @classmethod
    def _to_model(entity, row):
        """Convert a row of table data into a model"""
        model_columns = {}
        for (field_name, field) in entity.__fields__.items():
            column_name = field.field_info.extra.get('column')
            if column_name is not None:
                model_columns[field_name] = getattr(row, column_name)
        return entity(**model_columns)

    @classmethod
    def all(entity):
        results = db.fetchall(entity, entity.__table__.select())
        models = []
        for row in results:
            # Convert table result row into entity model
            models.append(entity._to_model(row))
        return models

    @classmethod
    def where(entity, column: str, value: Any):
        if 'where' not in entity.__query__: entity.__query__['where'] = []
        entity.__query__['where'].append({'column': column, 'value': value})
        return entity

    @classmethod
    def include(entity, *args):
        entity.__query__['include'] = list(args)
        return entity

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
    def get(entity):
        fields = entity.__fields__
        qb = entity.__query__
        table = entity.__table__
        selects = [table]
        joins = []

        # Add include
        if 'include' in qb:
            #>>> print(users.join(addresses))
            #users JOIN addresses ON users.id = addresses.user_id

            includes = qb['include']
            for include in qb['include']:
                field = fields.get(include)
                if not field: continue
                extra = field.field_info.extra

                # Ignore include if its an actual column
                if extra.get('column') is not None: continue

                # Handle one-to-one or many-to-one relations
                if 'has_one' in extra:
                    has_one = extra['has_one']
                    rel_model = None
                    rel_foreign_key = 'id'
                    rel_local_key = field.name + '_id'
                    if type(has_one) == tuple:
                        rel_model = has_one[0]
                        if len(has_one) >= 2:
                            rel_foreign_key = has_one[1]
                        if len(has_one) == 3:
                            rel_local_key = has_one[2]
                    else:
                        rel_model = has_one

                    # Get relations table
                    rel_table = rel_model.__table__
                    #dd(rel_model, rel_table, rel_foreign_key, rel_local_key)

                    # Add a join
                    join = sa.join(
                        left=table,
                        right=rel_table,
                        onclause=getattr(table.c, rel_local_key) == getattr(rel_table.c, rel_foreign_key)
                    )
                    joins.append(join)
                    selects.append(rel_table)

            # query = query.join(
            #     auth_users,
            #     table.c.creator_id == auth_users.c.id
            # )

            # j = join(user_table, address_table,
            #         user_table.c.id == address_table.c.user_id)
            # stmt = select([user_table]).select_from(j)

            #>>> print(users.join(addresses,
            #addresses.c.email_address.like(users.c.name + '%'))

        #query = table.select().select_from(j)
        #query = sa.select([table, auth_users]).select_from(j)
        #query = sa.select([table])
        if joins:
            #query = sa.select(selects).select_from(*joins)
            query = sa.select([
                table.c.id,
                table.c.unique_slug,
                table.c.title,

                rel_table.c.id.label('creator.id'),
                rel_table.c.email.label('creator.email')
            ]).select_from(*joins)
        else:
            query = sa.select(selects)

        # Add where
        if 'where' in entity.__query__:
            for where in entity.__query__['where']:
                query = query.where(getattr(table.c, where['column']) == where['value'])

# query = session.query(Domain.domain_name, Subdomain.subdomain_name, Title.title, Title.status, Title.response_len, Title.created_on, Title.updated_on)
# query = query.join(Title).join(Subdomain)

        #print(query)

        results = db.fetchall(entity, query)
        # for row in results:
        #     dd(row.items())

        # dd(results)

        models = []
        for row in results:
            models.append(entity._to_model(row))

        # Clear builder
        entity.__query__ = {}
        return models

    @classmethod
    def insert(entity, values: List):
        """Insert an array of models in bulk"""
        # Convert each entity into a dictionary of table data
        bulk = []
        for value in values:
            bulk.append(value._to_table())
        table = entity.__table__
        db.execute(entity, table.insert(), bulk)

    def save(self):
        table = self.__table__
        values = self._to_table()
        query = table.insert().values(**values)
        db.execute(self, query)

    def _to_table(self) -> Dict:
        """Convert an model entry into a dictionary matching the tables columns"""
        table_columns = {}
        for (key, value) in self.__dict__.items():
            field = self.__class__.__fields__.get(key)
            # Fixme, now to handle read_only field? If at all?
            column_name = field.field_info.extra.get('column')
            table_columns[column_name] = value
        return table_columns


# IoC Class Instance
Model: ModelInterface = uvicore.ioc.make('Model')

# Public API for import * and doc gens
__all__ = ['_Model', 'Model']
