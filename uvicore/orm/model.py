import uvicore
from uvicore import db
from typing import List, Dict, Any, Union
from pydantic import BaseModel
from .metaclass import ModelMetaclass


class _Model(BaseModel, metaclass=ModelMetaclass):

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
    def find(entity, id: Union[int,str]):
        table = entity.Db.table
        query = table.select().where(table.c.id == id)
        results = db.fetchone(entity, query)
        return entity(**results)

    @classmethod
    def all(entity) -> List:
        results = db.fetchall(entity, entity.__table__.select())
        rows = []
        for row in results:
            #rows.append(entity(**row))
            # Fixme, have to add mapper code here
            rows.append(entity(id=row.user_id, name=row.first_name))
            #x = entity(id=1, name='3')
            #dd(x)
            #rows.append(entity(user_id=row.user_id, first_name=row.first_name))
        return rows

    @classmethod
    def where(entity, column: str, value: Any):
        entity.Db.where.append({'column': column, 'value': value})
        return entity

    @classmethod
    def get(entity):
        table = entity.Db.table
        query = table.select()
        if entity.Db.where:
            for where in entity.Db.where:
                query = query.where(getattr(table.c, where['column']) == where['value'])
        results = db.fetchall(entity, query)
        rows = []
        for row in results:
            rows.append(entity(**row))

        # Clear builder
        entity.Db.where = []
        return rows


# IoC Class Instance
Model = uvicore.ioc.make('Model')

# Public API for import * and doc gens
__all__ = ['_Model', 'Model']
