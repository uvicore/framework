import uvicore
from fastapi import APIRouter as _FastAPIRouter
from uvicore.typing import Any, Type, List, Callable, Optional
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
        return self.router.include_router(router)

    def add_route(self, path: str, endpoint: Callable, *,
        response_model: Optional[Type[Any]] = None,
        name: Optional[str] = None,
        # self,
        # path: str,
        # endpoint: Callable,
        # *,
        # response_model: Optional[Type[Any]] = None,
        # status_code: int = 200,
        # tags: Optional[List[str]] = None,
        # dependencies: Optional[Sequence[params.Depends]] = None,
        # summary: Optional[str] = None,
        # description: Optional[str] = None,
        # response_description: str = "Successful Response",
        # responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        # deprecated: Optional[bool] = None,
        # methods: Optional[Union[Set[str], List[str]]] = None,
        # operation_id: Optional[str] = None,
        # response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
        # response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
        # response_model_by_alias: bool = True,
        # response_model_exclude_unset: bool = False,
        # response_model_exclude_defaults: bool = False,
        # response_model_exclude_none: bool = False,
        # include_in_schema: bool = True,
        # response_class: Optional[Type[Response]] = None,
        # name: Optional[str] = None,
        # route_class_override: Optional[Type[APIRoute]] = None,
        # callbacks: Optional[List[APIRoute]] = None,
    ) -> None:
        return self.router.add_api_route(
            path=path,
            endpoint=endpoint,
            response_model=response_model,
            name=name,
            # status_code=status_code,
            # tags=tags,
            # dependencies=dependencies,
            # summary=summary,
            # description=description,
            # response_description=response_description,
            # responses=responses,
            # deprecated=deprecated,
            # methods=methods,
            # operation_id=operation_id,
            # response_model_include=response_model_include,
            # response_model_exclude=response_model_exclude,
            # response_model_by_alias=response_model_by_alias,
            # response
        )

    # @property
    # def router(self):
    #     return self._router



# IoC Class Instance
#ApiRouter: RouterInterface = uvicore.ioc.make('ApiRouter', _ApiRouter)

# Public API for import * and doc gens
#__all__ = ['ApiRouter', '_ApiRouter']
