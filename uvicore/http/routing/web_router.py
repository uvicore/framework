from typing import Any, Callable, List, Type

from starlette.routing import BaseRoute
from starlette.routing import Router as _StarletteRouter

import uvicore
from uvicore.contracts import WebRouter as RouterInterface
from uvicore.support.dumper import dd, dump


# Example of just using the entier Starlette Router without abstraction
@uvicore.service()
class WebRouter(_StarletteRouter):

    # Add a GET route decorator to starlette
    def get(self,
        path: str,
        name: str = None,
    ) -> Callable:
        return self.route(
            path=path,
            name=name,
            methods=['GET'],
            include_in_schema=False,
        )

    # Add a POST route decorator to starlette
    def post(self,
        path: str,
        name: str = None,
    ) -> Callable:
        return self._router.route(
            path=path,
            name=name,
            methods=['POST'],
            include_in_schema=False,
        )

    # Add a PUT route decorator to starlette
    def put(self,
        path: str,
        name: str = None,
    ) -> Callable:
        return self._router.route(
            path=path,
            name=name,
            methods=['PUT'],
            include_in_schema=False,
        )

    # Add a PATCH route decorator to starlette
    def patch(self,
        path: str,
        name: str = None,
    ) -> Callable:
        return self._router.route(
            path=path,
            name=name,
            methods=['PATCH'],
            include_in_schema=False,
        )

    # Add a DELETE route decorator to starlette
    def delete(self,
        path: str,
        name: str = None,
    ) -> Callable:
        return self._router.route(
            path=path,
            name=name,
            methods=['DELETE'],
            include_in_schema=False,
        )

    # Add a OPTIONS route decorator to starlette
    def options(self,
        path: str,
        name: str = None,
    ) -> Callable:
        return self._router.route(
            path=path,
            name=name,
            methods=['OPTIONS'],
            include_in_schema=False,
        )

    # Add a HEAD route decorator to starlette
    def head(self,
        path: str,
        name: str = None,
    ) -> Callable:
        return self._router.route(
            path=path,
            name=name,
            methods=['HEAD'],
            include_in_schema=False,
        )

    # Add a TRACE route decorator to starlette
    def trace(self,
        path: str,
        name: str = None,
    ) -> Callable:
        return self._router.route(
            path=path,
            name=name,
            methods=['TRACE'],
            include_in_schema=False,
        )



# Example of making my own router abstraction
class WebRouterXXX(RouterInterface):

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

    def post(self,
        path: str,
        name: str = None,
    ) -> Callable:
        return self._router.route(
            path=path,
            name=name,
            methods=['POST']
        )

    # Not needed
    # def include_router(self, router: "WebRouter") -> None:
    #     # Starlette does not have a _router.include_router  like FastAPI
    #     # This manually adds each route in the router to starlette router
    #     for route in router.routes:
    #         self._router.routes.append(route)


# IoC Class Instance
#WebRouter: RouterInterface = uvicore.ioc.make('WebRouter', _WebRouter)

# Public API for import * and doc gens
#__all__ = ['WebRouter', '_WebRouter']
