from typing import Callable, List

from fastapi import FastAPI as _FastAPI
from starlette.types import ASGIApp

import uvicore
from uvicore.contracts import Server as ServerInterface
from uvicore.support.dumper import dd, dump

# This is our actual FastAPI Server
# Can only have one server, can't be both FastAPI and/or Starlette
# The FastAPI server inherits Starlette server but extends it with
# extra options for openapi, so we must use that as our base http app

# In classic FastAIP example, this is same as
# app = FastAPI(), but I call it app.http


class _Server(ServerInterface):
    # def controller(self, *args, **kargs):
    #     return self.include_router(*args, **kargs)

    _server: _FastAPI

    def __init__(self, debug: bool, title: str, version: str, openapi_url: str, docs_url: str, redoc_url: str):

        # Fireup FastAPI HTTP Core
        self._server = _FastAPI(
            debug=debug,
            title=title,
            version=version,
            openapi_url=openapi_url,
            docs_url=docs_url,
            redoc_url=redoc_url,
        )

    def include_router(self, router, *, prefix: str = '', tags: List[str] = None):
        self._server.include_router(
            router=router,
            prefix=prefix,
            tags=tags,
        )

    def mount(self, path: str, app: ASGIApp, name: str = None) -> None:
        self._server.mount(path=path, app=app, name=name)

    def on_event(self, event_type: str) -> Callable:
        return self._server.on_event(event_type)

    @property
    def server(self):
        return self._server
