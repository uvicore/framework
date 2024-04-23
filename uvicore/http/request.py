import json
from fastapi.security import SecurityScopes
from fastapi.params import Security as SecurityClass
from fastapi.datastructures import UploadFile, DefaultPlaceholder
from starlette.requests import Request, HTTPConnection, ClientDisconnect, cookie_parser

# NOTE, all params are also available at uvicore.http.params
# Difference between fastapi.params vs fastapi.param_functions??
# param_functions add more props and defaults then instantiate
# the param Class themselves.  Like a higher wrapper around the classes.
# All docs say 'from fastapi import Form' which actually comes from param_functions
from fastapi.param_functions import Path
from fastapi.param_functions import Query
from fastapi.param_functions import Header
from fastapi.param_functions import Cookie
from fastapi.param_functions import Body
from fastapi.param_functions import Form
from fastapi.param_functions import File
from fastapi.param_functions import Depends
from fastapi.param_functions import Security

class Parameter(SecurityClass):
    """Base class for user defined request parameters with infinite kwargs!"""

    # Parameters can accept any number of kwargs which are hacked as
    # a single "string" security scope converted to json then converted
    # back to an object before the handler is called

    #def __init__(self, scopes: Sequence[str] = []):
    def __init__(self, **kwargs):
        # Hack, scopes must be strings, convert kwargs into one JSON string
        scopes = [json.dumps(kwargs)]

        # Call FastAPI Security Depends with "self" and one scope as a JSON string
        super().__init__(dependency=self, scopes=scopes, use_cache=True)

    async def __call__(self, security_scopes: SecurityScopes, request: Request):
        # Hack, scopes are a JSON blog of kwargs
        kwargs = json.loads(security_scopes.scopes[0])

        # Call user defined handler
        return await self.handle(request=request, **kwargs)
