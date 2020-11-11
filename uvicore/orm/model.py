from typing import Any, Dict, Generic, List, Tuple, TypeVar, Union

from pydantic import BaseModel as PydanticBaseModel

import uvicore
from uvicore import contracts
from uvicore.orm.mapper import Mapper
from uvicore.orm.query import OrmQueryBuilder
from uvicore.support.classes import hybridmethod
from uvicore.support.dumper import dd, dump
from uvicore.support.collection import getvalue

# Keep for public import usage.
# Example: from uvicore.orm.model import Model, Metaclass, Field, BelongsTo...
from uvicore.orm.fields import BelongsTo, BelongsToMany, Field, HasMany, HasOne  # isort:skip
from uvicore.orm.metaclass import ModelMetaclass  # isort:skip

E = TypeVar("E")


# Any method here in the model WILL CLASH with your models field names
# But any method you add to the meteclass will NOT clash with fieldnames but cannot
# show up in an interface or code intellisense.
# So reserved field names are:
#   query
#   insert
#   insert_with_relations
#   mapper
#   create
#   save
#   delete
#   link
#   unlink
# and other items inside pydantic itself (list here???)


class _Model(Generic[E], PydanticBaseModel):

    def __init__(self, **data: Any) -> None:
        # Call pydantic parent
        super().__init__(**data)

        # Fill in callback properties
        for (key, callback) in self.__class__.__callbacks__.items():
            setattr(self, key, callback(self))

    @classmethod
    def query(entity) -> OrmQueryBuilder[OrmQueryBuilder, E]:
        return OrmQueryBuilder(entity)

    # These are nice, but they polute the namespace of FIELDS, so use just query()
    # @classmethod
    # async def get(entity) -> List[Any]:
    #     return await OrmQueryBuilder(entity).get()

    # @classmethod
    # async def find(entity, id: Any) -> Any:
    #     return await OrmQueryBuilder(entity).find(id)

    # @classmethod
    # def include(entity, *args):
    #     return OrmQueryBuilder(entity).include(*args)

    @classmethod
    async def insert(entity, models: Union[E, Dict, List[E], List[Dict]]) -> Any:
        """Insert one or more entities as List of entities or List of Dictionaries

        This bulk insert does NOT allow inserting child relations at the
        same time as there is no way to get each parents PK out to
        reference with each child in BULK. If you want to insert parent
        and relations at the same time use the slower non-bulk
        insert_with_relations() instead.
        """

        # Convert List[Model] or List[Dict] into dict of mapped table columns ready for insert
        bulk = entity.mapper(models).table()
        query = entity.table.insert()

        if type(bulk) == list:
            # List, so bulk insert
            return await entity.execute(query, bulk)
        else:
            # Single, so single insert, returning PK or silently passing if error
            try:
                return await entity.execute(query, bulk)
            except:
                pass

    @classmethod
    async def insert_with_relations(entity, models: List[Dict]) -> None:
        """Insert one or more entities as List of Dict that DO have relations included

        Because relations are included, this insert is NOT bulk and must
        loop each row, insert the parent, get the PK, then insert each
        children (or children first then parent depending on BelongsTo vs
        HasOne or HasMany)
        """

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
                if type(relation) == HasMany or type(relation) == HasOne or type(relation) == BelongsTo or type(relation) == BelongsToMany:
                    # Cannot change a dict in place or you get error
                    # RuntimeError: dictionary keys changed during iteration
                    # Se we'll add to a list and delete it outside the loop
                    relations[fieldname] = {
                        'relation': relation,
                        'data': value
                    }

            # Delete relations from parent model as they cannot be inserted
            for relation in relations.keys():
                del model[relation]

            # BelongTo relations are the inverse of HasOne or HasMany in that
            # the child has to be created BEFORE the parent
            for relation in relations.values():
                data = relation['data']
                relation = relation['relation']
                if type(relation) == BelongsTo:
                    # Because we insert the children first, skip inserting
                    # children later down the method
                    skip_children = True

                    # Recursively insert child and get PK
                    child_pk = await relation.entity.insert_with_relations([data])

                    # Replace parent foreignKey with child_pk
                    model[relation.local_key] = child_pk

            # Convert model Dict into actual Model instance
            model_instance = entity(**model)

            # Insert the parent model and retrieve parents new PK value
            model_instance = await model_instance.save()
            parent_pk = getattr(model_instance, entity.pk)

            # Don't insert children if we already did above with BelongsTo
            if not skip_children:
                # Now insert each file relation
                for relation in relations.values():
                    data = relation['data']
                    relation = relation['relation']
                    if type(relation) == HasMany or type(relation) == HasOne or type(relation) == BelongsTo:
                        childmodels = data
                        if type(childmodels) != list: childmodels = [childmodels]

                        # Handle One-To-Many
                        if type(relation) == HasMany or type(relation) == HasOne:
                            # Replace child foreignKey with parent_pk
                            for childmodel in childmodels:
                                childmodel[relation.foreign_key] = parent_pk

                        # We don't know if this child has its own children, so
                        # we must also insert_with_relations()
                        await relation.entity.insert_with_relations(childmodels)

                    elif type(relation) == BelongsToMany:
                        #dump(relation.name, data, model_instance)
                        #await entity.link(relation.name, data)
                        #await model_instance.link(relation.name, data)
                        await model_instance.create(relation.name, data)

            # Return parent_pk for recursion only
            # This method not meant to return anything valuable to the user
            return parent_pk

    @hybridmethod
    def mapper(self_or_entity, *args) -> Mapper:
        return Mapper(self_or_entity, *args)

    async def create(self, relation_name: str, models: Union[Any, List[Any]]) -> None:
        """Create related records and link them to this parent (self) model"""
        # Get the entity of this model instance (which is the metaclass, aka self.__class__)
        entity = self.__class__

        # Get field and relation info
        field = entity.modelfields.get(relation_name)
        relation = field.relation.fill(field)

        # Convert to list
        if type(models) != list: models = [models]

        # Assume each does not yet exists, so create all
        if type(relation) == HasMany:

            relation_field = relation.foreign_key
            relation_value = getattr(self, relation.local_key)

            # Fill in relation foreign key vlaue
            for model in models:
                model[relation_field] = relation_value

            # Bulk insert new values with proper keys
            await relation.entity.insert(models)

        # Cannot assume a record has been created or linked, so loop each and test
        elif type(relation) == BelongsToMany:
            for model in models:
                if type(model) == dict:
                    # Model is a Dictionary, convert to actual model
                    model = relation.entity(**model)

                # If its PK is set, it already exists
                create = getattr(model, relation.entity.pk) == None

                if create:
                    pk_value = await relation.entity.insert(model)
                    setattr(model, relation.entity.pk, pk_value)

                await self.link(relation_name, model)

    async def save(self) -> None:
        # Get the entity of this model instance (which is the metaclass, aka self.__class__)
        entity = self.__class__

        # Hum, think about this.  Probably a BAD idea.  Imagine you already have a record
        # and they change around relations, then type .save() would they expect ALL relations
        # to insert/delete/update properly?  I think not.  This .save() shouldn't work on relations
        # Pull out relations and try to insert/link them later
        # relations = {}
        # for fieldname in self.__dict__:
        #     field = entity.modelfields.get(fieldname)
        #     if not field: continue
        #     if not field.relation: continue
        #     data = getattr(self, fieldname)
        #     if data:
        #         relations[fieldname] = data
        #         #relation = field.relation.fill(field)
        #         # relations[fieldname] = {
        #         #     'relation': relation,
        #         #     'data': data
        #         # }

        # Convert self model instance into Dict of mapped table columns
        values = self.mapper().table()

        # Check if exists
        table = entity.table
        query = table.select().where(getattr(table.c, entity.pk) == getattr(self, entity.pk))
        exists = await entity.fetchone(query)

        if exists:
            # Record exists, perform update
            query = table.update().where(getattr(table.c, entity.pk) == getattr(self, entity.pk)).values(**values)
            await entity.execute(query)
        else:
            # New record, perform insert
            query = table.insert().values(**values)
            new_pk = await entity.execute(query)
            setattr(self, entity.pk, new_pk)

        # This is a TRY version if if exists, not sure which is more efficient, a select first, or an insert attempt/failure
        # try:
        #     # Try insert first
        #     query = table.insert().values(**values)
        #     new_pk = await entity.execute(query)
        #     setattr(self, entity.pk, new_pk)
        # except:
        #     # If fail, record already exists
        #     query = table.update().where(getattr(table.c, entity.pk) == getattr(self, entity.pk)).values(**values)
        #     await entity.execute(query)

        # # Insert relations
        # for relation_name, data in relations.items():
        #     await self.create(relation_name, data)

        # Return model with new PK value
        return self

    async def delete(self) -> None:
        # Get the entity of this model instance (which is the metaclass, aka self.__class__)
        entity = self.__class__

        # Delete this main (self) model record from the db
        table = entity.table
        query = table.delete().where(getattr(table.c, entity.pk) == getattr(self, entity.pk))
        await entity.execute(query)

    async def link(self, relation_name: str, models: Union[Any, List[Any]]) -> None:
        # Get the entity of this model instance (which is the metaclass, aka self.__class__)
        entity = self.__class__

        # Get field and relation info
        field = entity.modelfields.get(relation_name)
        relation = field.relation.fill(field)

        # Linking only works for Many-To-Many relations
        if type(relation) != BelongsToMany: raise Exception('Linking is for Many-To-Many relations only.')

        #dump(relation.entity.pk)
        #dump(field, relation)
        #dump('About to link these ' + relation_name, models, 'to this model', entity, 'on record with pk ' + str(pk), 'using pivot table ' + relation.join_tablename, '-------')

        # Insert linkage data one link at a time so we can gracefully skip duplicates
        if type(models) != list: models = [models]
        for model in models:
            # Set pivot relation data
            data = {
                relation.left_key: getvalue(self, entity.pk),
                relation.right_key: getvalue(model, relation.entity.pk)
            }

            # Try insert, fail silently if exists
            try:
                query = relation.join_table.insert().values(**data)
                await entity.execute(query)
            except:
                # Ignore Integrity Errors
                pass

    async def unlink(self, relation_name: str, models: Union[Any, List[Any]] = None) -> None:
        # Get the entity of this model instance (which is the metaclass, aka self.__class__)
        entity = self.__class__

        # Get field and relation info
        field = entity.modelfields.get(relation_name)
        relation = field.relation.fill(field)

        # Linking only works for Many-To-Many relations
        if type(relation) != BelongsToMany: raise Exception('Linking is for Many-To-Many relations only.')

        # Get table and start where on self ID
        table = relation.join_table
        query = table.delete().where(getattr(table.c, relation.left_key) == getattr(self, entity.pk))
        if models is not None:
            # Add in proper relation Ids
            if type(models) != list: models = [models]
            ids = [getvalue(x, relation.entity.pk) for x in models]
            query = query.where(getattr(table.c, relation.right_key).in_(ids))
        await entity.execute(query)


# IoC Class Instance
_ModelIoc: _Model = uvicore.ioc.make('Model', _Model)

# Actual Usable Model Class Derived from IoC Inheritence
#class Model(Generic[E], _BaseModel[E], ModelInterface[E], metaclass=ModelMetaclass):
class Model(Generic[E], _ModelIoc[E], contracts.Model[E]):
    pass

# Public API for import * and doc gens
#__all__ = ['_Model', 'Model']
