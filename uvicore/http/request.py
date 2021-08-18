import json
from fastapi.params import Security
from uvicore.typing import Sequence, List
from fastapi.security import SecurityScopes
from uvicore.support.dumper import dump, dd
from starlette.requests import Request, HTTPConnection
from fastapi.params import Path, Query, Header, Cookie, Body, Form, File, Depends, Security

class Parameter(Security):
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
