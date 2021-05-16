# #from uvicore.db import Model, sa
from uvicore import app, db
import pydantic
from pydantic import BaseModel, Field
from pydantic.fields import ModelField, FieldInfo
from pydantic.main import ModelMetaclass
import sqlalchemy as sa
from typing import Optional, List, Dict, Mapping, TypeVar, Union, Generic, Any
# from mreschke.wiki import db
from uvicore.support.dumper import dump, dd
from dataclasses import dataclass


# # Non-Default connection
# db.connection('con2').table('users')->where('name', 'John')->get()

# # Default connection assumed
# db.table('users')->get()
# db.table('users')->where('name', 'John')->get()

# # Show all connection information (from config + tables, engine...)
# db.connections()


# class User(db.Model):
#     #__tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(length=50))


# class UserSchema(Schema):
#     id: int
#     name: str

#     class Config:
#         orm_mode = True

E = TypeVar('E')


def xx():
    dump('hi')

class SimpleRepr(type):
    def __repr__(cls):
        return 'hi'




class EntityMetaclass(ModelMetaclass):

    def __new__(mcs, name, bases, namespace, **kwargs):
        # The cls from super() pydantic is the actual model class
        # id (models.user.User), not Entity.  We want to add __ properties
        # to that model class like pydantic does, so we add them to this
        # new_namespace and pass that into pydantic ModelMetaclass
        new_namespace = {
            '__connection__': None,
            '__tablename__': None,
            '__table__': None,
            '__callbacks__': {},
            **{n: v for n, v in namespace.items()},
        }

        # Call pydantic ModelMetaClass which builds __fields__ and more
        cls = super().__new__(mcs, name, bases, new_namespace, **kwargs)

        # Meta is fired up more than once, sometimes pydantic has NOT
        # actually populated all fields.  If no fields, ignore this __new__
        if not cls.__fields__: return cls

        dump("Registering Schema")

        # Dynamically Build SQLAlchemy Table From Model Properties
        if cls.__table__ is None:
            dump('Building SA Table From Model Properties')

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


class Entity(BaseModel, metaclass=EntityMetaclass):

    # __connection__ = None
    # __tablename__ = None
    # __table__ = None
    # __callbacks__ = {}
    #__registered__ = False

    # @classmethod
    # def table(entity):
    #     return entity.__table__

    def __init__(self, **data: Any) -> None:
        # Register SQLAlchemy table metadata for this connection only once
        #self.__table__()

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

    #     #title='Some Title',
    #     #description='Some Desc',
    #     default=42,
    #     readOnly=False,
    #     #sortable=True,
    #     #searchable=True,
    #     properties={
    #         'test': 'hi',
    #     }
    # )
        return {
            'connection': entity.__connection__,
            'tablename': entity.__tablename__,
            'table': entity.__table__,
            'fields': fields,
        }

    @classmethod
    def initX_MOVED_TO_METACLASS(entity):
        # Only register once

        if entity.__registered__ == True: return
        entity.__registered__ = True
        dump("Registering Schema")

        dump(__class__.__dict__)
        #dump(entity.__dict__)
        #dump(entity.__fields__['name'].field_info)

        # Dynamically Build SQLAlchemy Table From Model Properties
        if entity.__table__ is None:
            dump('Building SA Table From Model Properties')

            #(column, data) = [x for x in entity.__field_defaults__.items()]
            #dump(column)

                # All possibilities for ModelField()
                # name: str,
                # type_: Type[Any],
                # class_validators: Optional[Dict[str, Validator]],
                # model_config: Type['BaseConfig'],
                # default: Any = None,
                # default_factory: Optional[NoArgAnyCallable] = None,
                # required: 'BoolUndefined' = Undefined,
                # alias: str = None,
                # field_info: Optional[FieldInfo] = None,

            #dump(entity.__dict__)
            #dump(entity.name)

            # columns = [x for x in entity.__field_defaults__.values()]
            # __class__.__table__ = sa.Table(
            #     entity.__tablename__,
            #     db.metadata.get(entity.__connection__),
            #     *columns
            # )

        # Loop each field and perform manipulations
        for (key, field) in entity.__fields__.items():
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
                if 'callback' in extra:
                    callback = field.field_info.extra['callback']
                    # If callback is a string, assume a local method
                    if type(callback) == str:
                        callback = getattr(entity, callback)
                    entity.__callbacks__[key] = callback

                # Set full properties back to extra
                extra['properties'] = properties



            #dd(entity.__fields__['name'].field_info)

            # # Clone __field_defaults__ into our new __field__metadata__
            # entity.__field_metadata__ = dict(entity.__field_defaults__)
            # entity.__field_defaults__ = {}

            # # Set new __field_defaults__ and update __fields__
            # for (key, value) in entity.__field_metadata__.items():
            #     # Set new __field_defaults__
            #     entity.__field_defaults__[key] = value.default

            #     # Modify fields ModelField()
            #     entity.__fields__[key].default = value.default
            #     entity.__fields__[key].required = value.required

            #     # Make our own FieldInfo which FastAPI uses to display additional
            #     # data to our openapi JSON schema
            #     field_info = {}
            #     if value.default: field_info['default'] = value.default
            #     if value.title: field_info['title'] = value.title
            #     if value.description: field_info['description'] = value.description
            #     if value.read_only is not None: field_info['readOnly'] = value.read_only
            #     if value.write_only is not None: field_info['writeOnly'] = value.write_only
            #     entity.__fields__[key].field_info = FieldInfo(**field_info)

            #     # entity.__fields__[key].field_info = FieldInfo(
            #     #     default=value.default,
            #     #     title=value.title,
            #     #     description=value.description,
            #     #     readOnly=value.read_only,
            #     #     #writeOnly=value.
            #     #     # Properties is what FastAPI shows in openapi schema
            #     #     properties={
            #     #         'sortable': value.sortable,
            #     #         'searchable': value.searchable,
            #     #     }
            #     # )
            # dump(entity.__dict__)

            # # Build dictionary of properties with callbacks
            # for (key, meta) in entity.__field_metadata__.items():
            #     callback = meta.callback
            #     if callback is not None:
            #         # If callback is a string, assume a local method
            #         if type(callback) == str:
            #             callback = getattr(entity, meta.callback)
            #         entity.__callbacks__[key] = callback


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



    #.save()

    #@classmethod
    #def create(entity: E, List[E]):


class Meta:
    package: Any = None
    connection: str = None
    table: Any = None
    where: List = []


# class User2:
#     id: Optional[int] =

class Schema:
    __table__ = None

    def table(self):
        return __class__.__table__

    @classmethod
    def __schema__(self):
        if __class__.__table__ is None:
            # Build SA table
            dump('building sa table')
            attributes = [x for x in dir(self) if '__' not in x]
            columns = [getattr(self, x) for x in attributes]
            __class__.__table__ = sa.Table(
                self.__tablename__,
                db.metadata.get(self.__connection__),
                *columns
            )
        return __class__.__table__


class Field(FieldInfo):

    # def __init__(self, name: str = None, **kwargs: Any) -> None:
    #     # Pull out default column value
    #     default = kwargs.pop('default', None)

    #     # Set default property values
    #     if 'sortable' not in kwargs: kwargs['sortable'] = False
    #     if 'searchable' not in kwargs: kwargs['searchable'] = False

    #     # Call pydantic FieldInfo parent
    #     super().__init__(default, name=name, **kwargs)

    def __init__(self, name: str = None, *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        default: Optional[Any] = None,
        required: bool = False,
        sortable: bool = False,
        searchable: bool = False,
        read_only: Optional[bool] = None,
        write_only: Optional[bool] = None,
        callback: Optional[Any] = None,
        properties: Optional[Dict] = None,
    ):
        self.name: str = name
        self.title: str = title
        self.description: str = description
        self.default: Any = default
        self.required: bool = required
        self.sortable: bool = sortable
        self.searchable: bool = searchable
        self.read_only: Optional[bool] = read_only
        self.write_only: Optional[bool] = write_only
        self.callback: Any = callback
        self.properties: Optional[Dict] = properties
        super().__init__(
            default=default,
            column=name,
            title=title,
            description=description,
            required=required,
            sortable=sortable,
            searchable=searchable,
            readOnly=read_only,
            writeOnly=write_only,
            callback=callback,
            properties=properties,
        )


from mreschke.wiki.database.tables import users


class User(Entity):
    """Description, this shows up in openapi schemas section"""

    # Already have a table
    __connection__ = users.table['connection']
    __tablename__ = users.table['tablename']
    __table__ = users.table['schema']

    # Inline existing
    # __connection__ = 'wiki'
    # __tablename__ = 'users'
    # __table__ = sa.Table(
    #     __tablename__,
    #     db.metadata.get(__connection__),
    #     sa.Column("user_id", sa.Integer, primary_key=True),
    #     sa.Column("first_name", sa.String(length=50))
    # )

    # __table2__ = {
    #     # Existing
    #     'connection': users.table['connection'],
    #     'tablename': users.table['tablename'],
    #     'schema': users.table['schema'],

    #     # Not existing
    #     'connection': 'wiki',
    #     'tablename': 'users',
    #     'indexes': {
    #         'cluster': 'id',
    #         'single': ['name'],
    #         'composite': [
    #             ['id', 'name'],
    #             ['name', 'name2']
    #         ],
    #     }
    # }
    # __indexes__ = ['name']
    # __composites__ = [
    #     ['id', 'name']
    # ]

    # Auto columns
    # All tables get these auto columns unless a flag is False
    # creator_id, created_at
    # updator_id, updated_at
    # owner_id (owner can be different than creator)
    # is_deleted ??maybe

    # Auth system
    # auth needs to be its own package with its own connection string 'auth'
    # with many tables

    # Generic tables
    # Like django_admin_log ... I could also have a package of generic tables
    # for logging changes, a list of all models (django_content_type) for permission
    # polymorphism usage etc...even a list of packages like django app_label


    # Not permission GROUPS, but ROLES, which the wiki will COME WITH
    # These permissions are so generic using model perm strings
    # they could be implied if you don't override __roles__
    # Since roles are APP specific NOT PACKAGE specific
    # You can also override these elsewhere in your APP (config?)
    # Imagine including the wiki in your CRM and you want ALL users FULL ACCESS
    # Though I suppose you could just add all users to *_create, *_read, *_update, *_delete...
    # But maybe you want to tweak _owner, or _all, or _user, may still want override
    # But how to do object level permissions?  These are on the entity as a whole.  ??
    __roles__ = {
        # _user is anyone logged in
        # _all is anyone even those not logged in (public)
        # _owner is the owner of the record (could be different that creator_id field)
        'create': ['user_create'],
        'read': ['user_read', '_owner'],
        'update': ['user_update', '_owner'],
        'delete': ['user_delete', '_owner'],
    }
    # django model perms are add_user, change_user, delete_user, view_user
    # Mine generically could be user_create, user_read, user_update, user_delete


    # id: Optional[int]
    # name: str

    #id: Optional[int] = {'column': 'user_id', 'default': 'xyz'}
    #name: str = {'column': 'first_name', 'sortable': True}

    # id: Optional[int] = Field(
    #     42,
    #     #alias='id',
    #     title='some title',
    #     description='The users primary key',
    #     # See fastapi source models.py SchemaBase class for all possible attributes
    #     # that show up in the openapi spec
    #     readOnly=True,
    #     #writeOnly=True,
    #     properties={
    #         'db_column': 'user_id',
    #         'sortable': True,
    #         'searchable': True,
    #     },
    # )

    # name: str = Field(
    #     None,
    #     #alias='name',
    #     title='some title',
    #     description='The users name',
    #     properties={
    #         'db_column': 'first_name',
    #         'sortable': True,
    #         'searchable': True,
    #     },
    # )

    # name2: str = Field(
    #     None,
    #     #alias='name',
    #     title='some title',
    #     description='The users name',
    #     properties={
    #         'sortable': True,
    #         'searchable': True,
    #         'callback': '_name2'
    #     },
    # )

    # id: Optional[int] = {
    #     'default': 42,
    #     'required': True,  # defaults to false
    #     'title': 'some title',
    #     'description': 'The users primary key',
    #     'readOnly': True,
    #     'properties': {
    #         'db_column': 'user_id',
    #         'sortable': True,
    #         'searchable': True,
    #     },
    # }

    # name: str = {
    #     'default': None,
    #     'title': 'some title',
    #     'description': 'The users name',
    #     'properties': {
    #         'db_column': 'first_name',
    #         'sortable': True,
    #         'searchable': True,
    #     },
    # }

    # name2: str = {
    #     'default': None,
    #     'title': 'some title',
    #     'description': 'The users name',
    #     'properties': {
    #         'db_column': 'first_name',
    #         'sortable': True,
    #         'searchable': True,
    #         'callback': '_name2'
    #     },
    # }

    id: Optional[int] = Field('user_id',
        #title='Some Title',
        #description='Some Desc',
        default=42,
        read_only=True,
        #sortable=True,
        #searchable=True,
        properties={
            'test': 'hi',
        }
    )

    name: str = Field('first_name',
        title='Some Title',
        description='Some Desc',
        required=True,
        write_only=True,
    )

    name2: Optional[str] = Field(None,
        title='Some Title',
        description='Some Desc',
        callback='full_name',
    )


    def full_name(self):
        return 'Your ID is ' + str(self.id) + ", your name is " + self.name


    #__connection__ = 'wiki'
    #__tablename__ = 'users'


    # id: Optional[int] = sa.Column('user_id', sa.Integer,
    #     key='id',
    #     primary_key=True,
    #     info={
    #         'sortable': True,
    #         'searchable': False,
    #     }
    # )
    # name: str = sa.Column('first_name', sa.String(length=50),
    #     key='name',
    #     info={
    #         'sortable': True,
    #         'searchable': True,
    #     }
    # )

    # test_id: str = {
    #     'column': 'test_id',
    #     'type': 'string',
    #     'length': 50,
    #     'default': 'my default',
    #     'sortable': True,
    #     'filterable': True,
    #     'methods': ['create', 'read']
    # }

    # test_id2: str = Schema(
    #     column='test_id',
    #     type='string',
    #     length=50,
    #     default='my default',
    #     sortable=True,
    #     filterable=True,
    #     methods=['create', 'read']  # or view=False or read=False, or display=False
    # )


    def hi(self):
        return "Hi " + str(self.name)

    # class Meta(Schema):
    #     __connection__= 'wiki'
    #     __tablename__ = 'users'
    #     id = sa.Column('id', sa.Integer, primary_key=True)
    #     name = sa.Column('name', sa.String(length=50))





    # class Db(Meta):
    #     # SQLAlchemy Table
    #     #metadata = sa.MetaData()

    #     # Because the db config is in the wiki package I also
    #     # need to know the actual package
    #     # so package + which connection, if no connection, use default
    #     package = app.package('wiki')
    #     connection = 'wiki'

    #     # We must be able to use the db without a Model
    #     # Even without a table definition.  Imagine connecting to some random
    #     # database, you don't have a Model or a sa.Table(), you just want to query it
    #     # based on a connection. Preferably with the query builder AND raw
    #     #db.select(table)
    #     #db.con('wiki').select(table)

    #     table = sa.Table(
    #         "usersx",
    #         db.metadata.get(connection),
    #         sa.Column("id", sa.Integer, primary_key=True),
    #         sa.Column("name", sa.String(length=50))
    #     )

# Init class to register SQLAlchemy table metadata
#User.init()



from abc import ABCMeta
class MyMeta(ABCMeta):
    def __new__(mcs, name, bases, namespace, **kwargs):
        fields: Dict = {}


        new_namespace = {
            '__fields__': fields,
        }
        cls = super().__new__(mcs, name, bases, new_namespace, **kwargs)
        return cls


class User2(metaclass=MyMeta):
    pass

#dd(User2.__dict__)
