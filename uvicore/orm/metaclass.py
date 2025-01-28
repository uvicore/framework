import uvicore
from uvicore.orm.fields import Field
from uvicore.support.dumper import dd, dump
from prettyprinter import pretty_call, register_pretty
from pydantic.fields import FieldInfo as PydanticFieldInfo
from pydantic.main import ModelMetaclass as PydanticMetaclass
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union, Sequence

import sqlalchemy as sa

# try:
# except ImportError:  # pragma: nocover
#     pass
#     #sa = None  # type: ignore
#     #ClauseElement = None  # type: ignore


# Think of this metaclass as all the STATIC methods similar to @classmethod
# but different in that they become INVISIBLE to the instance of the class
# which is ideal so pydantic doesn't see these and clobber any actual 'fields'
# that have the same name.  This means I can have a field called 'email' and a
# true static class method called `email()` and pydantic won't complain.  I can use
# the static via User.email() and the instatnce from user.email.
# See https://stackoverflow.com/questions/59341761/what-are-the-differences-between-a-classmethod-and-a-metaclass-method
# for a detailed difference between using @classmethod for statics vs a metaclass


@uvicore.service()
class ModelMetaclass(PydanticMetaclass):

    # Testing of duplicate field
    # Only works if EACH model sets a metaclass=ModelMetaclass
    # You cannot set the metaclass at the Module.py level
    # def email(entity):
    #     return 'email on meta'

    # def slug(entity):
    #     return 'slug on meta'


    # Remember all metaclass method ARE @classmethods
    # Remember any method here DO NOT clash with pydantic field names
    # Remember any method here do NOT show up in code intellisense because its a metaclass
    #   If you want it in code intellisense, it must be in model.py and ModelInterface
    #   but then it WILL clash with any pydantic fields of the same name.
    # Basically anything here should be used privately from inside the ORM.
    #   If any method is to be public (either as a @classmethod Post. or instance method post.
    #   it should go in model.py and be in the ModelInterface



    ############################################################################
    ## These query builder passthroughs are for convenience only.  Best to use
    ## MyModel.query().get()... instead (the query() is on the Model.py not
    ## this metaclass).  Why use query()?  Becuase metaclasses are not currently
    ## supported in VSCode for autocomplete code intellisense but parent classes
    ## are.  So by using query() you get autocomplete on the full query builder!
    ############################################################################
    # async def get(entity) -> List[Any]:
    #     """Query builder passthrough"""
    #     return await OrmQueryBuilder(entity).get()

    # async def find(entity, id: Any) -> Any:
    #     """Query builder passthrough"""
    #     return await OrmQueryBuilder(entity).find(id)

    # def where(entity, column: Union[str, List[Tuple]], operator: str = None, value: Any = None):
    #     """Query builder passthrough"""
    #     return OrmQueryBuilder(entity).where(column, operator, value)

    # def or_where(entity, wheres: List):
    #     """Query builder passthrough"""
    #     return OrmQueryBuilder(entity).or_where(wheres)

    # def include(entity, *args):
    #     """Query builder passthrough"""
    #     return OrmQueryBuilder(entity).include(*args)
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

    @property
    def modelname(entity) -> str:
        return entity.__name__

    @property
    def modelfqn(entity) -> str:
        module = entity.__module__
        if module is None or module == str.__module__:
            return entity.__name__  # Avoid reporting __builtin__
        else:
            return module + '.' + entity.__name__

    def modelfield(entity, fieldname: str) -> Field:
        field = entity.modelfields.get(fieldname)
        if not field: raise Exception("Field {} not found in model {}".format(fieldname, entity.modelfqn))
        return field

    async def execute(entity, query: Any, values: Optional[Sequence[Mapping[str, Any]] | Mapping[str, Any]] = None) -> sa.CursorResult:
        """Database execute in the context of this entities connection"""
        return await uvicore.db.execute(query=query, values=values, connection=entity.__connection__)

    async def fetchall(entity, query: sa.Select|str, values: Optional[Sequence[Mapping[str, Any]] | Mapping[str, Any]] = None) -> Sequence[sa.Row]:
        """Database fetchall in the context of this entities connection"""
        return await uvicore.db.fetchall(query=query, connection=entity.__connection__)

    async def fetchone(entity, query: sa.Select|str, values: Optional[Sequence[Mapping[str, Any]] | Mapping[str, Any]] = None) -> sa.Row|None:
        """Database fetchone in the context of this entities connection"""
        return await uvicore.db.fetchone(query=query, connection=entity.__connection__)

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

    def selectable_columns(entity, table: sa.Table = None, *, show_writeonly: Union[bool, List] = False) -> List[sa.Column]:
        """Get all SQLA columns that are selectable

        Why not just use the table to get all columns?  Because a table
        may have far more columns than the actual model.  So we use the model
        to infer a list of actual SQLA columns (excluding write_only fields)
        """
        if table is None: table = entity.table

        # Not all models require tables (databaseless models)
        if table is None: return []

        all_columns = table.columns
        columns: List[sa.Column] = []
        for (field_name, field) in entity.modelfields.items():
            # Exclude None columns (which are relations) and write_only columns which cannot be viewed
            if field.column:
                show = False
                if not field.write_only: show = True
                if type(show_writeonly) == bool:
                    # show_writeonly is a bool, meaning show all writeonly fields
                    if field.write_only and show_writeonly == True: show = True
                else:
                    # show_writeonly is a list of fields to allow
                    if field.write_only and field.column in show_writeonly: show = True

                if show:
                    columns.append(getattr(all_columns, field.column))
        return columns

    def info(entity) -> Dict[str, Any]:
        fields = {}
        for (field_name, field) in entity.modelfields.items():
            fields[field_name] = field
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

        # Pull out all model properties of type Field() and store in __modelfields__ property
        # Then replace the original properties from Field() to Pydantics FieldInfo(), converting some Field() arguments
        # into 'x-tra' arguments for FieldInfo()
        # In the end, __modelfields__ are the original uvicore Field() that you defined in the model
        # and the original model fields are replaced with pydantics FieldInfo().  Later when I call super().__new__
        # pydantic further converts by MOVING the actual class properties into __fields__ and changing from FieldInfo to ModelField
        __modelfields__: Dict[str, Field] = {}
        for field_name, field in namespace.items():
            if field_name[0] != '_' and type(field) == Field:
                # Pull out uvicore model Field() into own __modelfields__ dict
                field.name = field_name
                __modelfields__[field_name] = field

                # Derive extra field information for pydantics FieldInfo OpenAPI schema generation
                #dump(getattr(namespace, field_name))

                # Convert uvicore model field into pydantic FieldInfo
                # Be careful what you pipe into PydanticFieldInfo() as these show up in the OpenAPI schema
                # from FastAPI 0.65.0+ because in their openapi/models.py they set class Config extra='allow'
                # by default.  Which means any item you put in PydanticFieldInfo that is not a keyword on that class
                # goes into extra *kwargs and extra now shows up in openapi.json.  The problem with that is valid
                # OpenAPI only allows certain keywords, see https://swagger.io/docs/specification/data-models/keywords/
                # In fact, the 'properties' I was using for a catch-all JSON blog is totally invalid.  Its not a ignored blog
                # its a nested schame field properties.  The only valid way to add extra ignored fields to a schema is to
                # prefix them with x-  see https://swagger.io/specification/#specification-extensions

                # For some dumb reason I was also piping EVERY thing into PydanticFieldInfo, even callback, evaluate
                # and relation.  Which now that extra=allow those were all trying to be parsed by FastAPI json_encoder
                # which totally broke everything.  So I need to be more strategic which uvicore Field() items I pump into
                # Pydantic FieldInfo().  I added a fields_passed_to_pydantic_FieldInfo in my Field class that contains a
                # List of valid properties to pass into PydanticFieldInfo()

                field_info_kwargs = {}
                #dump(field.__annotations__)
                for slot in field.__annotations__.keys():
                    value = getattr(field, slot)
                    if value is None: continue;

                    # Only pipe certain uvicore Field properties into pydantics FieldInfo or you get invalid OpenAPI spec
                    if slot in Field.__valid_oepnapi_keywords__:
                        arg = slot

                        # Convert some understores to camelCase for OpenAPI keyword compatibility
                        if slot == 'read_only': arg = 'readOnly'
                        if slot == 'write_only': arg = 'writeOnly'
                        if slot == 'min_length': arg = 'minLength'
                        if slot == 'max_length': arg = 'maxLength'
                        field_info_kwargs[arg] = value

                    elif slot in Field.__convert_to_extensions__:
                        # Convert these Field() arguments to the x-tra Dict
                        # See https://swagger.io/specification/#specification-extensions
                        if 'x-tra' not in field_info_kwargs: field_info_kwargs['x-tra'] = {}
                        if slot == 'properties':
                            field_info_kwargs['x-tra'] = {**field_info_kwargs['x-tra'], **getattr(field, slot)}
                        else:
                            field_info_kwargs['x-tra'][slot] = getattr(field, slot)

                #dump(field_info_kwargs)
                namespace[field_name] = PydanticFieldInfo(**field_info_kwargs)
                #dump(namespace[field_name])

        #dump(namespace)

        # If we extend and overwrite our own models, then some information
        # will be buried in the bases tuple.  Loop each base and
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

        #dd(new_namespace)

        # Call pydantic ModelMetaClass
        # Amoung other things, pydantic will take all model attributes that do not
        # begin with a _ and convert them into ModelField classes
        # This is why I keep the originals in my new __modelfields__ attribute
        cls = super().__new__(mcls, name, bases, new_namespace, **kwargs)
        #dump(name, cls, cls.__dict__, '-----------------------------')

        # Meta is fired up more than once, sometimes pydantic has NOT
        # actually populated all fields.  If no fields, ignore rest of this custom __new__
        if not cls.__fields__: return cls

        # Pretty Printer
        # Register a pretty printer just for this entity.  Why not on the main
        # Model class itself?  Because then it prints each record as if it were
        # uvicore.orm.model.Model instead of the actual model class (ie: uvicore.auth.models.user.User)
        @register_pretty(cls)
        def pretty_entity(value, ctx):
            return pretty_call(ctx, cls, **value.__dict__)

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

        # Pull out all callbacks from __modelfields__ and store in cls.__callbacks__ for future processing
        for (key, field) in cls.__modelfields__.items():
            if field.callback:
                callback = field.callback
                if type(callback) == str:
                    callback = getattr(cls, field.callback)
                cls.__callbacks__[key] = callback

        #dump(cls.__dict__)
        return cls


# IoC Class Instance
#ModelMetaclass: _ModelMetaclass = uvicore.ioc.make('ModelMetaclass', _ModelMetaclass)
