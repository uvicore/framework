import uvicore
from .query import QueryBuilder
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union
from pydantic.main import ModelMetaclass as PydanticMetaclass
from sqlalchemy.sql import ClauseElement
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
    # def email(entity):
    #     return 'email on meta'

    async def get(entity):
        """Query builder passthrough"""
        return await QueryBuilder(entity).get()

    async def find(entity, id: Any):
        """Query builder passthrough"""
        return await QueryBuilder(entity).find(id)

    def where(entity, column: Union[str, List[Tuple]], operator: str = None, value: Any = None):
        """Query builder passthrough"""
        return QueryBuilder(entity).where(column, operator, value)

    def or_where(entity, wheres: List):
        """Query builder passthrough"""
        return QueryBuilder(entity).or_where(wheres)

    async def insert(entity, values: List):
        """Insert one or more entities"""
        bulk = []
        for value in values:
            bulk.append(value._to_table())
        table = entity.__table__
        query = table.insert()
        await entity._execute(query, bulk)

    async def _execute(entity, query: Union[ClauseElement, str], values: Union[List, Dict] = None) -> Any:
        """Database execute in the context of this entities connection"""
        return await uvicore.db.execute(query=query, values=values, connection=entity.__connection__)

    async def _fetchone(entity, query: Union[ClauseElement, str], values: Dict = None) -> Optional[Mapping]:
        """Database fetchone in the context of this entities connection"""
        return await uvicore.db.fetchone(query=query, connection=entity.__connection__)

    async def _fetchall(entity, query: Union[ClauseElement, str], values: Dict = None) -> List[Mapping]:
        """Database fetchall in the context of this entities connection"""
        return await uvicore.db.fetchall(query=query, connection=entity.__connection__)

    def _to_model(entity, row):
        """Convert a row of table data into a model"""
        model_columns = {}
        for (field_name, field) in entity.__fields__.items():
            column_name = field.field_info.extra.get('column')
            if column_name is not None:
                model_columns[field_name] = getattr(row, column_name)
        return entity(**model_columns)

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
            'connection': uvicore.db.connection(entity.__connection__),
            'tablename': entity.__tablename__,
            'table': entity.__table__,
            'fields': fields,
        }

    def __new__(mcls: type, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any], **kwargs) -> type:
        # mcls is this ModelMetaclass itself
        # name is the string name of the child class, in this case '_Model' from model.py
        # bases is a tuple of parent used in the child (_Model) class, in this case (uvicore.contracts.model.Model, pydantic.main.BaseModel) it does not include this metaclass
        # namespace is the child _Model classes original __dict__ Dictionary

        # Add my own ORM attributes to pydantics base ModelMetaClass
        new_namespace = {
            '__connection__': None,
            '__tablename__': None,
            '__table__': None,
            '__tableclass__': None,
            '__callbacks__': {},
            #'__query__': {},
            #'_test1': 'hi',
            **{n: v for n, v in namespace.items()},
        }

        # Call pydantic ModelMetaClass which builds __fields__ and more
        cls = super().__new__(mcls, name, bases, new_namespace, **kwargs)

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
                    properties['sortable'] = extra['sortable']
                    #del extra['sortable']
                #else:
                    #extra['sortable'] = False

                if 'searchable' in extra:
                    properties['searchable'] = extra['searchable']
                    #del extra['searchable']
                #else:
                    #extra['searchable']

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
ModelMetaclass: _ModelMetaclass = uvicore.ioc.make('ModelMetaclass')
