#from sqlalchemy.ext.declarative import declarative_base
import functools
import sqlalchemy
from sqlalchemy import event, orm
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from typing import Any
# from typing import Iterator, Any
# from functools import lru_cache
# from fastapi_utils.session import FastAPISessionMaker
from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy.ext.declarative import as_declarative, declared_attr
# from sqlalchemy.orm import Session

# #Model = declarative_base()
# #Model = sa.ext.declarative.declarative_base()

# # def get_db() -> Iterator[Session]:
# #     """ FastAPI dependency that provides a sqlalchemy session """
# #     yield from _sessionmaker().get_db()


# # @lru_cache()
# # def _sessionmaker() -> FastAPISessionMaker:
# #     """ This function could be replaced with a global variable if preferred """
# #     #database_uri = DBSettings().database_uri
# #     database_uri = "mysql://root:techie@127.0.0.1/uvicore_wiki"
# #     return FastAPISessionMaker(database_uri)


# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# engine = create_engine("mysql+pymysql://root:techie@127.0.0.1/uvicore_wiki")
# SessionLocal = sessionmaker(bind=engine)

# @as_declarative()
class Model2:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Model(object):
    """Base class for SQLAlchemy declarative base model.

    To define models, subclass :attr:`db.Model <SQLAlchemy.Model>`, not this
    class. To customize ``db.Model``, subclass this and pass it as
    ``model_class`` to :class:`SQLAlchemy`.
    """

    #: Query class used by :attr:`query`. Defaults to
    # :class:`SQLAlchemy.Query`, which defaults to :class:`BaseQuery`.
    query_class = None

    #: Convenience property to query the database for instances of this model
    # using the current session. Equivalent to ``db.session.query(Model)``
    # unless :attr:`query_class` has been changed.
    query = None

    def __repr__(self):
        identity = inspect(self).identity
        if identity is None:
            pk = "(transient {0})".format(id(self))
        else:
            pk = ', '.join(to_str(value) for value in identity)
        return '<{0} {1}>'.format(type(self).__name__, pk)

class BaseQuery(orm.Query):

    def xx(self):
        return 'xx'


def _make_table(db):
    def _make_table(*args, **kwargs):
        if len(args) > 1 and isinstance(args[1], db.Column):
            args = (args[0], db.metadata) + args[1:]
        info = kwargs.pop('info', None) or {}
        info.setdefault('bind_key', None)
        kwargs['info'] = info
        return sqlalchemy.Table(*args, **kwargs)
    return _make_table

def _wrap_with_default_query_class(fn, cls):
    @functools.wraps(fn)
    def newfn(*args, **kwargs):
        _set_default_query_class(kwargs, cls)
        if "backref" in kwargs:
            backref = kwargs['backref']
            if isinstance(backref, string_types):
                backref = (backref, {})
            _set_default_query_class(backref[1], cls)
        return fn(*args, **kwargs)
    return newfn

class _QueryProperty(object):
    def __init__(self, sa):
        self.sa = sa

    def __get__(self, obj, type):
        try:
            mapper = orm.class_mapper(type)
            if mapper:
                return type.query_class(mapper, session=self.sa.session())
        except UnmappedClassError:
            return None

class SQLAlchemy(object):

    def __init__(self, query_class=BaseQuery, model_class=Model2, metadata=None):
        self.engine = self.__create_engine()
        self.Query = query_class
        self.session = orm.sessionmaker(bind=self.engine)
        self.Model = self.make_declarative_base(model_class, metadata)
        self.__include_sqlalchemy(query_class)

    def make_declarative_base(self, model, metadata=None):
        if not isinstance(model, DeclarativeMeta):
            model = declarative_base(
                cls=model,
                name='Model',
                metadata=metadata,
                #metaclass=DefaultMeta
            )
        if metadata is not None and model.metadata is not metadata:
            model.metadata = metadata

        if not getattr(model, 'query_class', None):
            model.query_class = self.Query

        model.query = _QueryProperty(self)
        return model

    def __include_sqlalchemy(self, cls):
        for module in sqlalchemy, sqlalchemy.orm:
            for key in module.__all__:
                if not hasattr(self, key):
                    setattr(self, key, getattr(module, key))
        # Note: self.Table does not attempt to be a SQLAlchemy Table class.
        self.Table = _make_table(self)
        self.relationship = _wrap_with_default_query_class(self.relationship, cls)
        self.relation = _wrap_with_default_query_class(self.relation, cls)
        self.dynamic_loader = _wrap_with_default_query_class(self.dynamic_loader, cls)
        self.event = event

    def create_all(self):
        self.Model.metedata.create_all(bind=self.engine)

    def __create_engine(self):
        return sqlalchemy.create_engine("mysql+pymysql://root:techie@127.0.0.1/uvicore_wiki")
