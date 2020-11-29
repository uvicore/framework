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

# Bound from service provider instead of decorator


@uvicore.service('uvicore.http.server._Server',
    aliases=['http', 'HTTP'],
    singleton=True,
    kwargs={
        'debug': uvicore.config('app.debug'),
        'title': uvicore.config('app.openapi.title'),
        'version': uvicore.app.version,
        'openapi_url': uvicore.config('app.openapi.url'),
        'docs_url': uvicore.config('app.openapi.docs_url'),
        'redoc_url': uvicore.config('app.openapi.redoc_url'),
    },
)
class _Server(ServerInterface):
    """HTTP Server private class.

    Do not import from this location.
    Use the uvicore.app.http singleton global instead."""

    @property
    def server(self) -> _FastAPI:
        return self._server

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

    def include_router(self, router, *, prefix: str = '', tags: List[str] = None) -> None:
        self._server.include_router(
            router=router,
            prefix=prefix,
            tags=tags,
        )

    def mount(self, path: str, app: ASGIApp, name: str = None) -> None:
        self._server.mount(path=path, app=app, name=name)

    def on_event(self, event_type: str) -> Callable:
        return self._server.on_event(event_type)


# IoC Class Instance
# No because not to be used by the public
#Server: ServerInterface = uvicore.ioc.make('Http')

# Public API for import * and doc gens
#__all__ = ['_Server']
