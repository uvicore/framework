import uvicore
from fastapi import APIRouter as _FastAPIRouter
from typing import Any, Type, List, Callable
from starlette.routing import BaseRoute
from uvicore.contracts import ApiRouter as RouterInterface


@uvicore.service()
class ApiRouter(RouterInterface):

    @property
    def router(self) -> _FastAPIRouter:
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
        # Fireup FastAPI Router
        self._router = _FastAPIRouter()

    def get(self,
        path: str,
        name: str = None,
        *,
        response_model: Type[Any] = None,
        include_in_schema: bool = True
    ) -> Callable:
        return self._router.get(
            path=path,
            name=name,
            response_model=response_model,
            include_in_schema=include_in_schema,
        )

    #def include_router(self, router: "APIRouter", *, prefix: str = '', tags: List[str] = None) -> None:
    def include_router(self, router: "APIRouter") -> None:
        # Only used for the class based controller
        # return self._router.include_router(router,
        #     prefix=prefix,
        #     tags=tags
        # )
        return self._router.include_router(router)

    # @property
    # def router(self):
    #     return self._router



# IoC Class Instance
#ApiRouter: RouterInterface = uvicore.ioc.make('ApiRouter', _ApiRouter)

# Public API for import * and doc gens
#__all__ = ['ApiRouter', '_ApiRouter']
