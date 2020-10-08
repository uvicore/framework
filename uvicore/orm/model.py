from typing import Any, Dict, Generic, List, Tuple, TypeVar, Union

from pydantic import BaseModel as PydanticBaseModel

import uvicore
from uvicore.contracts import Model as ModelInterface
from uvicore.orm.fields import BelongsTo, Field, HasMany, HasOne
from uvicore.orm.mapper import Mapper
from uvicore.orm.metaclass import ModelMetaclass
from uvicore.orm.query import OrmQueryBuilder
from uvicore.support.classes import hybridmethod
from uvicore.support.dumper import dd, dump

E = TypeVar("E")

#class _Model(Generic[E], ModelInterface, PydanticBaseModel):
class _BaseModel(Generic[E], PydanticBaseModel):
#class Model(Generic[E], PydanticBaseModel, metaclass=ModelMetaclass):
#class _Model(PydanticBaseModel):

    def __init__(self, **data: Any) -> None:
        # Call pydantic parent
        super().__init__(**data)

        # Fill in callback properties
        for (key, callback) in self.__class__.__callbacks__.items():
            setattr(self, key, callback(self))

    @classmethod
    def query(entity) -> OrmQueryBuilder[OrmQueryBuilder, E]:
        return OrmQueryBuilder(entity)

    @classmethod
    async def insert(entity, models: Union[List[E], List[Dict]]) -> None:
        # Convert List[Model] or List[Dict] into dict of mapped table columns ready for insert
        bulk = entity.mapper(models).table()
        query = entity.table.insert()
        await entity.execute(query, bulk)

    @classmethod
    async def insert_with_relations(entity, models: List[Dict]) -> None:
        # Note about bulk insert with nested relations Dictionary
        # Bulk insert does not give back the primary keys for each inserted record
        # So I have no way to know the PK of the parent when I insert the child relations
        # So the only way to possibly insert parent and child is to do one at a time
        # which is not bulk and will be slower.  If I wanted to do this I could pull
        # out all models that HAVE a relation and set those asside.  All that do NOT
        # have a relation I could bulk insert, then after insert one those that do have a
        # relation one at a time.  The problem with this is they won't be inserted in the
        # order you wanted.  Only way to preserve order is to check if ANY models have
        # a relation, if so, loop and insert one at a time, no bulk period.
        # SQLAlchemy does have a bulk_save_objects that does return the PKs but
        # encode/databases does not impliment this.  Instead their insert_many
        # uses a cursor where each row is added as a query, then the cursor is committed.
        # This is bulk insert, but no way to retrieve each PK from it.

        bulk = []
        for model in models:

            # Check each field for relations and rename them before inserting parent
            relations = {}
            skip_children = False
            for (fieldname, value) in model.items():
                field = entity.modelfields.get(fieldname)
                if not field: continue
                if not field.relation: continue
                relation = field.relation.fill(field)
                if type(relation) == HasMany or type(relation) == HasOne or type(relation) == BelongsTo:
                    # Cannot change a dict in place or you get error
                    # RuntimeError: dictionary keys changed during iteration
                    # Se we'll add to a list and delete it outside the loop
                    relations[fieldname] = relation
                    relation.data = value

            # Delete relations from parent model as they cannot be inserted
            for relation in relations.keys():
                del model[relation]

            # BelongTo relations are the inverse of HasOne or HasMany in that
            # the child has to be created BEFORE the parent
            for relation in relations.values():
                if type(relation) == BelongsTo:
                    # Because we insert the children first, skip inserting
                    # children later down the method
                    skip_children = True

                    # Recursively insert child and get PK
                    child_pk = await relation.entity.insert_with_relations([relation.data])

                    # Replace parent foreignKey with child_pk
                    model[relation.local_key] = child_pk

            # Convert model Dict into table Dict
            tabledata = entity.mapper(model).table()

            # Insert the parent model
            query = entity.table.insert()
            parent_pk = await entity.execute(query, tabledata)

            # Don't insert children if we already did above with BelongsTo
            if not skip_children:
                # Now insert each file relation
                for relation in relations.values():
                    if type(relation) == HasMany or type(relation) == HasOne or type(relation) == BelongsTo:
                        childmodels = relation.data
                        if type(childmodels) != list: childmodels = [childmodels]

                        # Handle One-To-Many
                        if type(relation) == HasMany or type(relation) == HasOne:
                            # Replace child foreignKey with parent_pk
                            for childmodel in childmodels:
                                childmodel[relation.foreign_key] = parent_pk

                        # We don't know if this child has its own children, so
                        # we must also insert_with_relations()
                        await relation.entity.insert_with_relations(childmodels)

            # Return parent_pk for recursion only
            # This method not meant to return anything valuable to the user
            return parent_pk

    @hybridmethod
    def mapper(self_or_entity, *args) -> Mapper:
        return Mapper(self_or_entity, *args)

    async def create(self, relation: str, values: Union[List[Dict], Dict]) -> None:
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
        # Convert self model instance into Dict of mapped table columns
        values = self.mapper().table()

        # FIXME: figure out UPSERT
        table = self.__class__.table
        query = table.insert().values(**values)
        new_pk = await self.__class__.execute(query)
        setattr(self, self.__class__.pk, new_pk)

    async def delete(self) -> None:
        dump('delete', self)
        pass

    async def link(self, relation: str, values: List):
        """Link ManyToMany values to this model"""
        query = OrmQueryBuilder(self)
        await query.link(relation, values)


# IoC Class Instance
_Model: _BaseModel = uvicore.ioc.make('Model', _BaseModel)


# Actual Usable Model Class Derived from IoC Inheritence
#class Model(Generic[E], _BaseModel[E], ModelInterface[E], metaclass=ModelMetaclass):
class Model(Generic[E], _Model[E], ModelInterface[E]):
    pass


# Public API for import * and doc gens
#__all__ = ['_Model', 'Model']
