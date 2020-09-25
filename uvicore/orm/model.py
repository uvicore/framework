import uvicore
from typing import Any, Dict, Generic, TypeVar, List, Union, Tuple
from pydantic import BaseModel as PydanticBaseModel
from uvicore.contracts import Model as ModelInterface
from uvicore.support.dumper import dd, dump
from .query import QueryBuilder
from uvicore.orm.metaclass import ModelMetaclass
from uvicore.orm.fields import HasMany

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

    async def create(self, relation: str, values: Union[List[Dict], Dict]) -> Any:
        """Create related records and link them to the parent model"""
        field = self.__class__.modelfields.get(relation)
        relation = field.relation.fill(field)

        # Only works with HasMany or or HasOne
        # But NOT from the other way around (BelongsTo)
        # and not for ManyToMany
        if type(relation) == HasMany:
            relation_field = relation.foreign_key
            relation_value = getattr(self, relation.local_key)

            # Fill in relation foreign key vlaue
            for value in values:
                value[relation_field] = relation_value

        # Bulk insert new values with proper keys
        await relation.entity.insert(values)

    async def save(self) -> None:
        """Save this model to the database"""
        table = self.__table__
        values = self.to_table()
        query = table.insert().values(**values)
        new_pk = await self.__class__.execute(query)
        setattr(self, self.__class__.pk, new_pk)

    async def delete(self):
        """Delete this model from the database"""
        pass

    async def link(self, relation: str, values: List):
        """Link ManyToMany values to this model"""
        query = QueryBuilder(self)
        await query.link(relation, values)

    def to_table(self) -> Dict:
        """Convert an model entry into a dictionary matching the tables columns"""
        columns = {}
        for (field, value) in self.__dict__.items():
            field = self.__class__.modelfields.get(field)
            if field.column and not field.read_only:
                columns[field.column] = value
        return columns
        # table_columns = {}
        # for (key, value) in self.__dict__.items():
        #     field = self.__class__.__fields__.get(key)
        #     extra = field.field_info.extra
        #     column_name = extra.get('column')
        #     if column_name and not extra.get('readOnly'):
        #         table_columns[column_name] = value
        # return table_columns


# IoC Class Instance
# Model class cannot be from IoC if you want code intellisense to work
# NO Model: _Model = uvicore.ioc.make('Model', _Model)

# Public API for import * and doc gens
#__all__ = ['_Model', 'Model']
