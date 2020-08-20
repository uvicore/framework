from pydantic.main import ModelMetaclass as BaseMetaclass
from uvicore.support.dumper import dump, dd


class ModelMetaclass(BaseMetaclass):

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

        #dump("Registering Schema in Metaclass")

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

