# Uvicore custom
import warnings
from .authentication import Authentication

# Starlette passthrough via class proxy
from starlette.middleware.base import BaseHTTPMiddleware as _Base
from starlette.middleware.cors import CORSMiddleware as _CORS
from starlette.middleware.gzip import GZipMiddleware as _Gzip
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware as _HTTPSRedirect
from starlette.middleware.sessions import SessionMiddleware as _Session
from starlette.middleware.trustedhost import TrustedHostMiddleware as _TrustedHost

# starlette.middleware.wsgi is a deprecation shim in Starlette 1.x that warns on
# import.  Suppress that warning here so merely importing the framework stays quiet;
# a2wsgi is the recommended replacement if real WSGI mounting is ever needed.
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
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
