from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

import sqlalchemy as sa
from pydantic.fields import FieldInfo as PydanticFieldInfo
from pydantic.main import ModelMetaclass as PydanticMetaclass
from sqlalchemy.sql import ClauseElement

import uvicore
from uvicore.orm.fields import Field
from uvicore.orm.mapper import Mapper
from uvicore.orm.query import OrmQueryBuilder
from uvicore.support.dumper import dd, dump

# Think of this metaclass as all the STATIC methods similar to @classmethod
# but different in that they become INVISIBLE to the instance of the class
# which is ideal so pydantic doesn't see these and clobber any actual 'fields'
# that have the same name.  This means I can have a field called 'email' and a
# true static class method called `email()` and pydantic won't complain.  I can use
# the static via User.email() and the instatnce from user.email.
# See https://stackoverflow.com/questions/59341761/what-are-the-differences-between-a-classmethod-and-a-metaclass-method
# for a detailed difference between using @classmethod for statics vs a metaclass

class _ModelMetaclass(PydanticMetaclass):

    # Testing of duplicate field
    # Only works if EACH model sets a metaclass=ModelMetaclass
    # You cannot set the metaclass at the Module.py level
    def email(entity):
        return 'email on meta'

    def slug(entity):
        return 'slug on meta'


    # Remember all metaclass method ARE @classmethods
    # Remember any method here DO NOT clash with pydantic field names
    # Remember any method here do NOT show up in code intellisense because its a metaclass
    # If you want it in code intellisense, it myst be in model.py and ModelInterface
    # but then it WILL clash with any pydantic fields of the same name.


    ############################################################################
    ## These query builder passthroughs are for convenience only.  Best to use
    ## MyModel.query().get()... instead (the query() is on the Model.py not
    ## this metaclass).  Why use query()?  Becuase metaclasses are not currently
    ## supported in VSCode for autocomplete code intellisense but parent classes
    ## are.  So by using query() you get autocomplete on the full query builder!
    ############################################################################
    async def get(entity) -> List[Any]:
        """Query builder passthrough"""
        return await OrmQueryBuilder(entity).get()

    async def find(entity, id: Any) -> Any:
        """Query builder passthrough"""
        return await OrmQueryBuilder(entity).find(id)

    def where(entity, column: Union[str, List[Tuple]], operator: str = None, value: Any = None):
        """Query builder passthrough"""
        return OrmQueryBuilder(entity).where(column, operator, value)

    def or_where(entity, wheres: List):
        """Query builder passthrough"""
        return OrmQueryBuilder(entity).or_where(wheres)

    def include(entity, *args):
        """Query builder passthrough"""
        return OrmQueryBuilder(entity).include(*args)
    ############################################################################
    ############################################################################



    @property
    def pk(entity) -> str:
        """Get the entities primary key"""
        for field in entity.modelfields.values():
            if field.primary: return field.name

    @property
    def connection(entity) -> str:
        """Helper for entity connection string"""
        return entity.__connection__

    @property
    def tablename(entity) -> str:
        """Helper for entity tablename string"""
        return entity.__tablename__

    @property
    def table(entity) -> sa.Table:
        """Helper for entity SQLAlchemy table"""
        return entity.__table__

    @property
    def modelfields(entity) -> Dict[str, Field]:
        """Helper for original uvicore model fields (not pydantic __fields__)"""
        return entity.__modelfields__

    async def execute(entity, query: Union[ClauseElement, str], values: Union[List, Dict] = None) -> Any:
        """Database execute in the context of this entities connection"""
        return await uvicore.db.execute(query=query, values=values, connection=entity.__connection__)

    async def fetchone(entity, query: Union[ClauseElement, str], values: Dict = None) -> Optional[Mapping]:
        """Database fetchone in the context of this entities connection"""
        return await uvicore.db.fetchone(query=query, connection=entity.__connection__)

    async def fetchall(entity, query: Union[ClauseElement, str], values: Dict = None) -> List[Mapping]:
        """Database fetchall in the context of this entities connection"""
        return await uvicore.db.fetchall(query=query, connection=entity.__connection__)

    # def to_model(entity, row, prefix: str = None) -> Any:
    #     """Convert a row of table data into a model"""
    #     fields = {}
    #     for field in entity.modelfields.values():
    #         if not field.column: continue
    #         column = field.column
    #         if prefix: column = prefix + '.' + column
    #         if hasattr(row, column):
    #             fields[field.name] = getattr(row, column)
    #     return entity(**fields)

    # def to_column(entity, fieldname: str):
    #     """Convert a model field name into a table column name"""
    #     field = entity.modelfields.get(fieldname)
    #     if field: return field.column
    #     return fieldname

    def selectable_columns(entity) -> List[sa.Column]:
        """Get all SQLA columns that are selectable

        Why not just use the table to get all columns?  Because a table
        may have far more columns than the actual model.  So we use the model
        to infer a list of actual SQLA columns (excluding write_only fields)
        """
        all_columns = entity.table.columns
        columns: List[sa.Column] = []
        for (field_name, field) in entity.modelfields.items():
            if field.column and not field.write_only:
                columns.append(getattr(all_columns, field.column))
        return columns

    def info(entity, detailed: bool = False) -> Dict[str, Any]:
        fields = {}
        for (field_name, field) in entity.modelfields.items():
            info = field.field_info
            extra = info.extra
            fields[field_name] = {
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
                fields[field_name]['class_dict'] = entity.__dict__
                fields[field_name]['field_info'] = info,
                fields[field_name]['extra'] = extra,

        return {
            'connection': uvicore.db.connection(entity.__connection__),
            'tablename': entity.tablename,
            'table': entity.table,
            'fields': fields,
        }

    def __new__(mcls: type, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any], **kwargs) -> type:
        # mcls is this ModelMetaclass itself
        # name is the string name of the child class, in this case '_Model' from model.py
        # bases is a tuple of parent used in the child (_Model) class, in this case (uvicore.contracts.model.Model, pydantic.main.BaseModel) it does not include this metaclass
        # namespace is the child _Model classes original __dict__ Dictionary

        # Define our custom attributes
        __connection__ = None
        __tablename__ = None
        __table__ = None
        __tableclass__ = None
        __callbacks__ = {}

        # Pull out all properties of type Field and store in _fields property
        # And SWAP my Field for pydantics FieldInfo so pydantic knows how to handle each field
        # Do not confuse my custom __modelfields__ with pydantics __fields__
        __modelfields__: Dict[str, Field] = {}
        for field_name, field in namespace.items():
            if field_name[0] != '_' and type(field) == Field:
                # Pull out uvicore model field into own __modelfields__ dict
                field.name = field_name
                __modelfields__[field_name] = field

                # Convert uvicore model field into pydantic FieldInfo
                field_info_kwargs = {}
                for slot in field.__slots__:
                    arg = slot
                    if slot == 'read_only': arg = 'readOnly'
                    if slot == 'write_only': arg = 'writeOnly'
                    field_info_kwargs[arg] = getattr(field, slot)
                namespace[field_name] = PydanticFieldInfo(**field_info_kwargs)

        # If we extend and overwrite our own models, then some information
        # will be buried in the baseclass typle.  Loop each baseclass and
        # pluck out these critical fields (for modelfields, APPEND them to allow extension)
        for base in bases:
            if hasattr(base, '__modelfields__'):
                # Notice we are APPEND modelfields to allow model extension
                __modelfields__ = {**base.__modelfields__, **__modelfields__}

            # I am only setting these if not already set.  This allows a higher base
            # like the parent to override and win over the base children
            if hasattr(base, '__connection__') and not __connection__:
                __connection__ = base.__connection__
            if hasattr(base, '__tablename__') and not __tablename__:
                __tablename__ = base.__tablename__
            if hasattr(base, '__table__') and not __table__:
                __table__ = base.__table__
            if hasattr(base, '__tableclass__') and not __tableclass__:
                __tableclass__ = base.__tableclass__
            if hasattr(base, '__callbacks__') and not __callbacks__:
                __callbacks__ = base.__callbacks__

        # Add my own ORM attributes to pydantics base ModelMetaClass
        new_namespace = {
            '__connection__': __connection__,
            '__tablename__': __tablename__,
            '__table__': __table__,
            '__tableclass__': __tableclass__,
            '__callbacks__': __callbacks__,
            '__modelfields__': __modelfields__,
            #'__query__': {},
            #'_test1': 'hi',
            **{n: v for n, v in namespace.items()},
        }

        # Call pydantic ModelMetaClass
        # Amoung other things, pydantic will take all model attributes that do not
        # begin with a _ and convert them into ModelField classes
        # This is why I keep the originals in my new __modelfields__ attribute
        cls = super().__new__(mcls, name, bases, new_namespace, **kwargs)

        #dump(cls.__dict__)



        # Meta is fired up more than once, sometimes pydantic has NOT
        # actually populated all fields.  If no fields, ignore this __new__
        if not cls.__fields__: return cls

        #dump("Registering Schema in Metaclass")

        # Build connection, tablename and table from tableclass
        if cls.__tableclass__ is not None:
            if cls.__connection__ is None: cls.__connection__ = cls.__tableclass__.connection
            if cls.__tablename__ is None: cls.__tablename__ = cls.__tableclass__.name
            if cls.__table__ is None: cls.__table__ = cls.__tableclass__.schema


        # Dynamically Build SQLAlchemy Table From Model Properties
        if cls.__table__ is not None:
            pass
            # Set connection and table name from table class
            #dd(cls.__table__.metadata.__dict__)
            #dd(dir(cls.__table__))
            #if cls.__connection__ is None: cls.__connection__ = cls.__table__.connection
            #if cls.__tablename__ is None: cls.__tablename__ = cls.__table__.name

        else:
            pass
            #dump('Building SA Table From Model Properties')
            # Fixme, code could go here to dynamically build
            # an SQLAlchemy table here.

            # An example of basic build, but fix to use __fields__
            # and each fields .field_info instead, and convert each model
            # property Field() into SA table stuff like columns and indexes...
            # columns = [x for x in entity.__field_defaults__.values()]
            # __class__.__table__ = sa.Table(
            #     entity.__tablename__,
            #     db.metadata.get(entity.__connection__),
            #     *columns
            # )

        # Loop each field and perform manipulations
        for (key, field) in cls.__fields__.items():
            if field.field_info is not None:
                extra = field.field_info.extra
                properties = extra.get('properties') or {}

                # Convert required from extra to proper ModelField override
                if 'required' in extra:
                    field.required = extra['required']
                    # Remove requires as it messes up FastAPI when passed on
                    del extra['required']

                # Add these keys into the properties dictionary to show in OpenAPI schema
                if 'sortable' in extra:
                    # Nullable boolean.  If None is omitted from OpenAPI
                    # If explicitely set to True or False, it will show in OpenAPI
                    if extra['sortable'] is not None:
                        properties['sortable'] = extra['sortable']

                if 'searchable' in extra:
                    # Nullable boolean.  If None is omitted from OpenAPI
                    # If explicitely set to True or False, it will show in OpenAPI
                    if extra['searchable'] is not None:
                        properties['searchable'] = extra['searchable']

                # Add in properties to extra
                if properties:
                    extra['properties'] = properties

                # Track properties with callbacks
                if 'callback' in extra and extra['callback'] is not None:
                    callback = field.field_info.extra['callback']
                    # If callback is a string, assume a local method
                    if type(callback) == str:
                        callback = getattr(cls, callback)
                    cls.__callbacks__[key] = callback

        #dump(cls.__dict__)
        return cls


# IoC Class Instance
ModelMetaclass: _ModelMetaclass = uvicore.ioc.make('ModelMetaclass', _ModelMetaclass)
