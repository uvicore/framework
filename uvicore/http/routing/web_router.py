from typing import Any, Callable, List, Type

from starlette.routing import BaseRoute
from starlette.routing import Router as _StarletteRouter

import uvicore
from uvicore.contracts import WebRouter as RouterInterface
from uvicore.support.dumper import dd, dump


@uvicore.service()
class WebRouter(RouterInterface):

    @property
    def router(self) -> _StarletteRouter:
        return self._router

    @property
    def routes(self) -> List[BaseRoute]:
        return self._router.routes

    @property
    def on_startup(self) -> None:
        return self._router.on_startup

    @property
    def on_shutdown(self) -> None:
        return self._router.on_shutdown

    def __init__(self):
        # Fireup Starlette Router
        self._router = _StarletteRouter()

    def get(self,
        path: str,
        name: str = None,
    ) -> Callable:
        return self._router.route(
            path=path,
            name=name,
            methods=['GET']
        )

    def include_router(self, router: "WebRouter") -> None:
        # Starlette does not have a _router.include_router  like FastAPI
        # This manually adds each route in the router to starlette router
        for route in router.routes:
            self._router.routes.append(route)


# IoC Class Instance
#WebRouter: RouterInterface = uvicore.ioc.make('WebRouter', _WebRouter)

# Public API for import * and doc gens
#__all__ = ['WebRouter', '_WebRouter']
