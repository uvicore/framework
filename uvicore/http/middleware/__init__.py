# Uvicore custom
from .authentication import Authentication

# Starlette passthrough via class proxy
from starlette.middleware.base import BaseHTTPMiddleware as _Base
from starlette.middleware.cors import CORSMiddleware as _CORS
from starlette.middleware.gzip import GZipMiddleware as _Gzip
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware as _HTTPSRedirect
from starlette.middleware.sessions import SessionMiddleware as _Session
from starlette.middleware.trustedhost import TrustedHostMiddleware as _TrustedHost
from starlette.middleware.wsgi import WSGIMiddleware as _WSGI


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
