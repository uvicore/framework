import uvicore
from typing import Any, Dict, Generic, TypeVar, List, Union, Tuple
from pydantic import BaseModel as PydanticBaseModel
from uvicore.contracts import Model as ModelInterface
from uvicore.support.dumper import dd, dump
from .query import QueryBuilder
from uvicore.orm.metaclass import ModelMetaclass


E = TypeVar("E")


#class _Model(Generic[E], ModelInterface, PydanticBaseModel):
class Model(Generic[E], PydanticBaseModel):
#class Model(Generic[E], PydanticBaseModel, metaclass=ModelMetaclass):
#class _Model(PydanticBaseModel):

    def __init__(self, **data: Any) -> None:
        # Call pydantic parent
        super().__init__(**data)

        # Fill in callback properties
        for (key, callback) in self.__class__.__callbacks__.items():
            setattr(self, key, callback(self))

    # @classmethod
    # def email(self, id: Any) -> E:
    #     return self

    @classmethod
    def query(entity) -> QueryBuilder[E]:
        return QueryBuilder[entity](entity)

    @classmethod
    async def insert(entity, values: List) -> Any:
        """Insert one or more entities"""
        bulk = []
        for value in values:
            bulk.append(value.to_table())
        query = entity.table.insert()
        await entity.execute(query, bulk)

    async def save(self):
        """Save this model to the database"""
        table = self.__table__
        values = self.to_table()
        query = table.insert().values(**values)
        await self._execute(query)

    async def delete(self):
        """Delete this model from the database"""
        pass

    def to_table(self) -> Dict:
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
# Model class cannot be from IoC if you want code intellisense to work
# NO Model: _Model = uvicore.ioc.make('Model', _Model)

# Public API for import * and doc gens
#__all__ = ['_Model', 'Model']
