from .security import Security

# Starlette
from starlette.middleware.authentication import AuthenticationMiddleware as _Authentication
from starlette.middleware.base import BaseHTTPMiddleware as _Base
from starlette.middleware.cors import CORSMiddleware as _CORS
from starlette.middleware.gzip import GZipMiddleware as _Gzip
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware as _HTTPSRedirect
from starlette.middleware.sessions import SessionMiddleware as _Session
from starlette.middleware.trustedhost import TrustedHostMiddleware as _TrustedHost
from starlette.middleware.wsgi import WSGIMiddleware as _WSGI
#from starlette.middleware.errors import ServerErrorMiddleware as _ServerError # NO, starlette adds LAST for us


class Authentication(_Authentication):
    pass

class Middleware(_Base):
    pass

class CORS(_CORS):
    pass

class Gzip(_Gzip):
    pass

class HTTPSRedirect(_HTTPSRedirect):
    pass

class Session(_Session):
    pass

class TrustedHost(_TrustedHost):
    pass

class WSGI(_WSGI):
    pass
