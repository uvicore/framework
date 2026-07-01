import uvicore
import warnings
from uvicore.orm.fields import Field
from uvicore.support.dumper import dd, dump
from uvicore.support.printer import pretty_call, register_pretty
from pydantic.fields import FieldInfo as PydanticFieldInfo
from pydantic._internal._model_construction import ModelMetaclass as PydanticMetaclass
from typing import Any, Dict, List, Mapping, Tuple, Sequence

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

    async def execute(entity, query: Any, values: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None) -> sa.CursorResult:
        """Database execute in the context of this entities connection"""
        return await uvicore.db.execute(query=query, values=values, connection=entity.__connection__)

    async def fetchall(entity, query: sa.Select|str, values: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None) -> Sequence[sa.Row]:
        """Database fetchall in the context of this entities connection"""
        return await uvicore.db.fetchall(query=query, connection=entity.__connection__)

    async def fetchone(entity, query: sa.Select|str, values: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None) -> sa.Row|None:
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

    def selectable_columns(entity, table: sa.Table = None, *, show_writeonly: bool | List = False) -> List[sa.Column]:
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

                # Convert uvicore model field into a Pydantic v2 FieldInfo.
                # Valid v2 FieldInfo kwargs (title, description, default, min_length,
                # max_length) are passed directly.  'example' (Pydantic v1, singular)
                # becomes 'examples' (v2, a list).  Non-standard JSON-schema keys
                # (readOnly/writeOnly and the x-tra "specification extensions") are NOT
                # FieldInfo kwargs in v2 — they go into json_schema_extra, which Pydantic
                # merges verbatim into the generated OpenAPI/JSON schema.
                # See https://swagger.io/docs/specification/data-models/keywords/ and
                # https://swagger.io/specification/#specification-extensions
                field_info_kwargs = {}
                json_schema_extra = {}
                for slot in field.__annotations__.keys():
                    value = getattr(field, slot)
                    if value is None: continue

                    if slot in Field.__valid_oepnapi_keywords__:
                        if slot == 'example':
                            field_info_kwargs['examples'] = [value]
                        elif slot == 'read_only':
                            json_schema_extra['readOnly'] = value
                        elif slot == 'write_only':
                            json_schema_extra['writeOnly'] = value
                        else:
                            # title, description, default, min_length, max_length
                            field_info_kwargs[slot] = value

                    elif slot in Field.__convert_to_extensions__:
                        # Convert these Field() arguments to the x-tra Dict
                        if 'x-tra' not in json_schema_extra: json_schema_extra['x-tra'] = {}
                        if slot == 'properties':
                            json_schema_extra['x-tra'] = {**json_schema_extra['x-tra'], **getattr(field, slot)}
                        else:
                            json_schema_extra['x-tra'][slot] = getattr(field, slot)

                # Pydantic v2: Optional[x] no longer implies a default.  Uvicore models
                # are DB-row containers routinely instantiated from a PARTIAL set of
                # columns (see Mapper), so every field must remain optional.  Default to
                # None unless the uvicore Field() declared an explicit default — this
                # preserves the Pydantic v1 ORM behavior where Optional fields defaulted
                # to None automatically.
                if 'default' not in field_info_kwargs:
                    field_info_kwargs['default'] = None

                if json_schema_extra:
                    field_info_kwargs['json_schema_extra'] = json_schema_extra

                namespace[field_name] = PydanticFieldInfo(**field_info_kwargs)

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
        #
        # Suppress Pydantic v2's "Field name 'x' shadows an attribute in parent" warning.
        # By design, Uvicore exposes ORM helpers (info, table, pk, connection, ...) as
        # metaclass methods specifically so they DON'T collide with real model field names
        # of the same name (e.g. a model field named 'info').  Pydantic v2 still emits a
        # warning for the name overlap even though it is intentional and harmless here.
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', message=r'Field name .* shadows an attribute in parent.*')
            cls = super().__new__(mcls, name, bases, new_namespace, **kwargs)
        #dump(name, cls, cls.__dict__, '-----------------------------')

        # Meta is fired up more than once, sometimes pydantic has NOT
        # actually populated all fields.  If no fields, ignore rest of this custom __new__
        # (Pydantic v2: __fields__ -> model_fields)
        if not cls.model_fields: return cls

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


        # Inline table definition.
        # If __table__ is still a raw list of SQLAlchemy columns, the model defined its
        # schema INLINE (instead of pointing __tableclass__ at a Table class).  Build a
        # real sa.Table from that list now, mirroring uvicore.database.Table.__init__ so
        # inline tables behave identically to separate-file tables (shared metadata
        # association and connection table prefix).
        if type(cls.__table__) == list:
            if uvicore.db is None:
                raise Exception(
                    "Model '{}' defines an inline __table__ but the database has not been "
                    "initialized yet.  Inline-table models must be loaded after the database "
                    "bootstraps (register them with register_db_models() in your package "
                    "provider), or point __tableclass__ at a Table class instead.".format(name)
                )
            if not cls.__connection__ or not cls.__tablename__:
                raise Exception(
                    "Model '{}' defines an inline __table__ list and therefore must also "
                    "define __connection__ and __tablename__ (or use a __tableclass__).".format(name)
                )

            connection = uvicore.db.connection(cls.__connection__)
            metadata = uvicore.db.metadata(cls.__connection__)

            # Apply the connection's table prefix, exactly like the Table base class
            prefix = connection.prefix
            if prefix is not None:
                cls.__tablename__ = str(prefix) + cls.__tablename__

            # Only build an actual sa.Table for the sqlalchemy backend.  Optional
            # __table_kwargs__ on the model maps to sa.Table()'s **kwargs (the inline
            # equivalent of a Table class's schema_kwargs).
            if connection.backend == 'sqlalchemy':
                table_kwargs = getattr(cls, '__table_kwargs__', None) or {}
                cls.__table__ = sa.Table(
                    cls.__tablename__,
                    metadata,
                    *cls.__table__,
                    **table_kwargs,
                )

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
