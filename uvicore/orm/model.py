from typing import Any, Dict, Generic, List, Tuple, TypeVar, Union

from pydantic import BaseModel as PydanticBaseModel

import uvicore
import sqlalchemy as sa
from uvicore.contracts import Model as ModelInterface
from uvicore.orm.fields import (BelongsTo, BelongsToMany, Field, HasMany,
                                HasOne, MorphMany, MorphOne, MorphToMany)
from uvicore.orm.mapper import _Mapper
from uvicore.orm.query import _OrmQueryBuilder
from uvicore.support.classes import hybridmethod
from uvicore.support.collection import getvalue, setvalue
from uvicore.support.dumper import dd, dump

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


@uvicore.service()
class Model(Generic[E], PydanticBaseModel, ModelInterface[E]):

    def __init__(self, **data: Any) -> None:
        # Call pydantic parent
        super().__init__(**data)

        # Fill in callback properties
        for (key, callback) in self.__class__.__callbacks__.items():
            setattr(self, key, callback(self))

    @classmethod
    def query(entity) -> _OrmQueryBuilder[_OrmQueryBuilder, E]:
        return _OrmQueryBuilder(entity)

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

        # Convert any type of dict or list to an actual Model or List[Model]
        models = entity.mapper(models).model()

        # Loop each model and call the before_save hook
        if type(models) == list:
            for model in models:
                # Fire Models Pre-Save Hook
                await model._before_save()
        else:
            await models._after_save()

        # Convert List[Model] or List[Dict] into dict of mapped table columns ready for insert
        bulk = entity.mapper(models).table()
        query = entity.table.insert()

        result = None
        if type(bulk) == list:
            # List, so bulk insert
            result = await entity.execute(query, bulk)
        else:
            # Single, so single insert, returning PK or silently passing if error
            try:
                result = await entity.execute(query, bulk)
            except:
                pass

        # Loop each model and call the after_save hook
        if type(models) == list:
            for model in models:
                await model._after_save()
        else:
            await models._after_save()

        # Return insert results (if single will be PK)
        return result

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

        for model in models:
            # Check each field for relations and rename them before inserting parent
            relations = {}
            skip_children = False
            for (fieldname, value) in model.items():
                field = entity.modelfields.get(fieldname)  # Using direct dictionary to skip bad values in dict
                if not field: continue
                if not field.relation: continue
                relation = field.relation.fill(field)
                # if (
                #     type(relation) == HasMany or
                #     type(relation) == HasOne or
                #     type(relation) == BelongsTo or
                #     type(relation) == BelongsToMany or
                #     type(relation) == MorphOne
                # ):
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
            #model_instance = entity(**model)
            model_instance = entity.mapper(model).model()

            # Insert the parent model and retrieve parents new PK value
            model_instance = await model_instance.save()
            parent_pk = getattr(model_instance, entity.pk)

            # Now insert each child relation
            for relation in relations.values():
                data = relation['data']
                relation = relation['relation']
                childmodels = data
                if type(childmodels) != list: childmodels = [childmodels]

                # Insert BelongsTo (which is the only one that obeys skip_children)
                if type(relation) == BelongsTo and not skip_children:
                    await relation.entity.insert_with_relations(childmodels)

                # Insert HasMany or HasOne (which are basically the same)
                elif type(relation) == HasOne or type(relation) == HasMany:
                    # Replace child foreignKey with parent_pk
                    for childmodel in childmodels:
                        childmodel[relation.foreign_key] = parent_pk
                    await relation.entity.insert_with_relations(childmodels)

                # Insert Polymorphic OneToOne
                elif type(relation) == MorphOne or type(relation) == MorphMany:
                    for childmodel in childmodels:
                        childmodel[relation.foreign_type] = entity.tablename
                        childmodel[relation.foreign_key] = parent_pk
                    await relation.entity.insert_with_relations(childmodels)

                # Insert Many-To-Many
                elif type(relation) == BelongsToMany or type(relation) == MorphToMany:
                    # By using .create, we are both linking the records in the pivot/relation table
                    # and also createing the actual record if it does not exist
                    await model_instance.create(relation.name, data)

        # Return parent_pk for recursion only
        # This method not meant to return anything valuable to the user
        return parent_pk

    @hybridmethod
    def mapper(self_or_entity, *args) -> _Mapper:
        return _Mapper(self_or_entity, *args)

    async def set(self, relation_name: str, models: Union[Any, List[Any]]) -> None:
        # Same as create, except it deletes all first, so it sets the entire children

        # Get the entity of this model instance (which is the metaclass, aka self.__class__)
        entity = self.__class__

        # Get field and relation info
        field = entity.modelfield(relation_name)
        relation = field.relation.fill(field)

        if type(relation) == BelongsToMany or type(relation) == MorphToMany:
            # Delete does not work for these relations, only unlink
            await self.unlink(relation_name)
        else:
            # Delete works for these relations
            await self.delete(relation_name)
        await self.create(relation_name, models)

    async def add(self, relation_name: str, models: Union[Any, List[Any]]) -> None:
        # Alias to create
        await self.create(relation_name, models)

    async def create(self, relation_name: str, models: Union[Any, List[Any]]) -> None:
        """Create related child records and link them to this parent (self) model"""
        # Get the entity of this model instance (which is the metaclass, aka self.__class__)
        entity = self.__class__

        # Get field and relation info
        field = entity.modelfield(relation_name)
        relation = field.relation.fill(field)

        # Convert to list
        if type(models) != list: models = [models]

        # Assume each does not yet exists, so create all as BULK insert
        if type(relation) == HasOne or type(relation) == HasMany or type(relation) == MorphOne or type(relation) == MorphMany:
            # Fill in relation foreign key vlaue
            for model in models:
                # Set new relation value (works of model is a dict or a model class instance!)
                setvalue(model, relation.foreign_key, getattr(self, relation.local_key))

                if type(relation) == MorphOne or type(relation) == MorphMany:
                    # For Polymorphic relations, also set type column
                    setvalue(model, relation.foreign_type, entity.tablename)

                    # # Check for Data types in values to serialize
                    # dict_values = getvalue(relation, 'dict_value')
                    # if dict_values:
                    #     if type(dict_values) != list: dict_values = [dict_values]
                    #     for dict_value in dict_values:
                    #         value = getvalue(model, dict_value)
                    #         if type(value) == dict or type(value) == list:
                    #             value = str(value)
                    #         setvalue(model, dict_value, value)

            # Bulk insert new values with proper keys
            await relation.entity.insert(models)

        # Cannot assume a record has been created or linked, so loop each and test
        # Because of this, we cannot bulk insert
        elif type(relation) == BelongsToMany or type(relation) == MorphToMany:
            for model in models:
                # If its PK is set, it already exists
                create = getvalue(model, relation.entity.pk) == None
                if create:
                    pk_value = await relation.entity.insert(model)
                    setvalue(model, relation.entity.pk, pk_value)

                # Link in pivot table
                await self.link(relation_name, model)

        else:
            raise Exception('Creating children does not work for this type of relation.')

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

        # Fire Models Pre-Save Hook
        await self._before_save()

        # Convert self model instance into Dict of mapped table columns
        values = self.mapper().table()

        # Check if exists
        exists = None
        table = entity.table
        if getattr(self, entity.pk):
            query = sa.select([getattr(table.c, entity.mapper(entity.pk).column())]).select_from(table).where(getattr(table.c, entity.pk) == getattr(self, entity.pk))
            #query = table.select().where(getattr(table.c, entity.pk) == getattr(self, entity.pk))  # Don't select *
            exists = await entity.fetchone(query)  # Returns None if not exists

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

    async def delete(self, relation_name: str = None) -> None:
        # Get the entity of this model instance (which is the metaclass, aka self.__class__)
        entity = self.__class__

        # COMMENT on deleting children
        # Well it could only work for HasOne/MorphOne, or possibly HasMany.  But those tables can simply
        # be deleted manually image.find(1).delete() for example.  For others like BelongsToMany we don't ever want
        # to delete the record and it could be used by many other records through the pivot, so we use unlink() instead
        # and we can also manually delete it if we watned (tags.where(post=1).delete() etc...)
        # So not sure I want a delete() to handle children?  If so maybe just HasOne and MorphOne?  Because with HasMany
        # you would also have to speicy WHICH ones to delete, like post.delete('comments', [1,2,3]) etc...
        # With a HasOne/MorphOne you could at least do post.delete('image') and thats quicker than image.find(post=1).delete() manually?

        # Notice I have not yet added delete for HasMany (likd post comments).  May be a bit dangerous maybe?

        if relation_name is not None:
            # Deleting children, do NOT delete the parent after the children, this is children only
            field = entity.modelfield(relation_name)
            relation = field.relation.fill(field)
            rel_table = relation.entity.table

            # Notice this will all fail if the child has other constraints
            if type(relation) == HasOne:
                query = (rel_table
                    .delete()
                    .where(getattr(rel_table.c, relation.foreign_key) == getattr(self, entity.pk))
                )
                await entity.execute(query)

            elif type(relation) == MorphOne or type(relation) == MorphMany:
                query = (rel_table
                    .delete()
                    .where(getattr(rel_table.c, relation.foreign_type) == entity.tablename)
                    .where(getattr(rel_table.c, relation.foreign_key) == getattr(self, entity.pk))
                )
                await entity.execute(query)
            else:
                raise Exception('Deleteing children does not work for this type of relation.')

            # Not sure I should implement OneToMany as you would need to be able to pass in WHICH items to delete
            # but if you go through all that trouble to get the right children models to pass in, you could just
            # delete from the actual child yourself (comments.where(post=1).delete() for example)

        else:
            # Delete this main parent (self) model record from the db
            table = entity.table
            query = table.delete().where(getattr(table.c, entity.pk) == getattr(self, entity.pk))
            await entity.execute(query)

    async def link(self, relation_name: str, models: Union[Any, List[Any]]) -> None:
        # Get the entity of this model instance (which is the metaclass, aka self.__class__)
        entity = self.__class__

        # Get field and relation info
        field = entity.modelfield(relation_name)
        relation = field.relation.fill(field)

        # Ensure models are always a list
        if type(models) != list: models = [models]

        # Insert linkage data one link at a time so we can gracefully skip duplicates
        if type(relation) == BelongsToMany:
            for model in models:
                # Set pivot relation data
                left_key_value = getvalue(self, entity.pk)
                right_key_value = getvalue(model, relation.entity.pk)
                pivot = {
                    relation.left_key: left_key_value,
                    relation.right_key: right_key_value
                }

                # Check if exists.
                # The encode/databases layer does NOT abstract each backend DB libraries exceptions
                # into a common interface so You cannot catch generic IntegrityError.  So instead of a
                # try catch, I will see if the record exists manually first :( - See https://github.com/encode/databases/issues/162
                table = relation.join_table
                query = (
                    sa.select([getattr(table.c, relation.left_key)]).select_from(table)
                    .where(getattr(table.c, relation.left_key) == left_key_value)
                    .where(getattr(table.c, relation.right_key) == right_key_value)
                )
                exists = await entity.fetchone(query)  # Returns None if not exists

                if not exists:
                    query = relation.join_table.insert().values(**pivot)
                    await entity.execute(query)

                # # Try insert, fail silently if exists
                # try:
                #     query = relation.join_table.insert().values(**pivot)
                #     await entity.execute(query)
                # except:
                #     # Ignore Integrity Errors
                #     pass

        elif type(relation) == MorphToMany:
            for model in models:
                # Set polymorphic pivor relation data
                left_type_value = entity.tablename
                left_key_value = getvalue(self, entity.pk)
                right_key_value = getvalue(model, relation.entity.pk)
                pivot = {
                    relation.left_type: left_type_value,
                    relation.left_key: left_key_value,
                    relation.right_key: right_key_value
                }

                # Check if exists.
                # The encode/databases layer does NOT abstract each backend DB libraries exceptions
                # into a common interface so You cannot catch generic IntegrityError.  So instead of a
                # try catch, I will see if the record exists manually first :( - See https://github.com/encode/databases/issues/162
                table = relation.join_table
                query = (
                    sa.select([getattr(table.c, relation.left_type)]).select_from(table)
                    .where(getattr(table.c, relation.left_type) == left_type_value)
                    .where(getattr(table.c, relation.left_key) == left_key_value)
                    .where(getattr(table.c, relation.right_key) == right_key_value)
                )
                exists = await entity.fetchone(query)  # Returns None if not exists

                if not exists:
                    query = relation.join_table.insert().values(**pivot)
                    await entity.execute(query)


                # Try insert, fail silently if exists
                # try:
                #     query = relation.join_table.insert().values(**pivot)
                #     await entity.execute(query)
                # except pymysql.err.IntegrityError:
                #     # Ignore Integrity Errors
                #     pass

        else:
            # Linking only works for Many-To-Many relations
            raise Exception('Linking is for Many-To-Many relations only.')

    async def unlink(self, relation_name: str, models: Union[Any, List[Any]] = None) -> None:
        # Get the entity of this model instance (which is the metaclass, aka self.__class__)
        entity = self.__class__

        # Get field and relation info
        field = entity.modelfield(relation_name)
        relation = field.relation.fill(field)

        # Ensure model is a list
        if models is not None:
            if type(models) != list: models = [models]
            ids = [getvalue(x, relation.entity.pk) for x in models]

        if type(relation) == BelongsToMany:
            # Get table and start where on self ID
            table = relation.join_table
            query = table.delete().where(getattr(table.c, relation.left_key) == getattr(self, entity.pk))
            if models is not None:
                # Add in proper relation Ids
                query = query.where(getattr(table.c, relation.right_key).in_(ids))
            await entity.execute(query)

        elif type(relation) == MorphToMany:
            # Get table and start where on self ID
            table = relation.join_table
            query = (
                table.delete()
                .where(getattr(table.c, relation.left_type) == entity.tablename)
                .where(getattr(table.c, relation.left_key) == getvalue(self, entity.pk))
            )
            if models is not None:
                # Add in proper relation Ids
                query = query.where(getattr(table.c, relation.right_key).in_(ids))
            await entity.execute(query)
        else:
            raise Exception('Uninking is for Many-To-Many relations only.')

    async def _before_save(self):
        #dump('MODEL-HOOK-BEFORE-SAVE')

        # Dispatch Before Save Event
        event_name = self.__class__.modelfqn + '-BeforeSave'
        uvicore.events.dispatch(event_name, {'model': self})

    async def _after_save(self):
        #dump('MODEL-HOOK-AFTER-SAVE')

        # Dispatch Before Save Event
        event_name = self.__class__.modelfqn + '-AfterSave'
        uvicore.events.dispatch(event_name, {'model': self})





# IoC Class Instance
#_ModelIoc: _Model = uvicore.ioc.make('Model', _Model)

# Actual Usable Model Class Derived from IoC Inheritence
#class Model(Generic[E], _BaseModel[E], ModelInterface[E], metaclass=ModelMetaclass):
#class Model(Generic[E], _ModelIoc[E], contracts.Model[E]):
    #pass

# Public API for import * and doc gens
#__all__ = ['_Model', 'Model']
