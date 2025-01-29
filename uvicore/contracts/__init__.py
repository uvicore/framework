from .application import Application
from .cache import Cache
from .config import Config
from .dispatcher import Dispatcher
from .ioc import Binding, Ioc
from .job_dispatcher import JobDispatcher
from .job import Job
from .logger import Logger
from .package import Package
from .provider import Provider
from .template import Template
from .user_info import UserInfo
from .user_provider import UserProvider
from .authenticator import Authenticator
from .email import Email


# Optional imports based on installed modules
try:
    import sqlalchemy
    from .builder import DbQueryBuilder, OrmQueryBuilder, QueryBuilder
    from .connection import Connection
    from .database import Database
    from .field import Field
    from .mapper import Mapper
    from .model import Model
    from .relation import Relation
    from .auto_api import AutoApi
except ImportError:
    pass

try:
    import fastapi
    from .router import (ApiRoute, ApiRouter, ModelRouter, Router, Routes, WebRoute, WebRouter)
    from .server import Server
except ImportError:
    pass



#from .event import Event
#from .router import ApiRouter, WebRouter
#from .routes import Routes


# The contracts package uses a __init__.py because users will import these
# methods from their own apps and we want a nicer import which looks
# like - from uvicore.contracts import Model
