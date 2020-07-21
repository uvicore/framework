import inspect
from typing import Any, Callable, List, Type, TypeVar, Union, get_type_hints
from fastapi import Depends
from uvicore.http.routing import WebRouter
from pydantic.typing import is_classvar
from starlette.routing import Route, WebSocketRoute
import uvicore
from uvicore.support.dumper import dump, dd

T = TypeVar("T")

CBV_CLASS_KEY = "__cbv_class__"


def WebController(router: WebRouter) -> Callable[[Type[T]], Type[T]]:
    """
    This function returns a decorator that converts the decorated into a class-based view for the provided router.
    Any methods of the decorated class that are decorated as endpoints using the router provided to this function
    will become endpoints in the router. The first positional argument to the methods (typically `self`)
    will be populated with an instance created using FastAPI's dependency-injection.
    For more detail, review the documentation at
    https://fastapi-utils.davidmontague.xyz/user-guide/class-based-views/#the-cbv-decorator
    """

    def decorator(cls: Type[T]) -> Type[T]:
        return _cbv(router, cls)

    return decorator


def _cbv(router: WebRouter, cls: Type[T]) -> Type[T]:
    """
    Replaces any methods of the provided class `cls` that are endpoints of routes in `router` with updated
    function calls that will properly inject an instance of `cls`.
    """

    # Runs at END of controller, so "router" is my router in controller
    # with /about route and all
    #dd(router)
    # for route in router.routes:
    #     dump(route.path)
    # dd('done')

    # Adds any class decorated arguments to class attributes
    _init_cbv(cls)

    # New web router to replace "router" as defined in the controller
    cbv_router = WebRouter()

    # An array of tuples of each class method including the new __init__ from _init_cbv(cls) above
    function_members = inspect.getmembers(cls, inspect.isfunction)
    #dd(function_members)

    # A set of just the controller methods includeing new __init__
    functions_set = set(func for _, func in function_members)
    #dd(functions_set)

    # List of Route objects in class defined router
    # Basically pulling out each route from my original class
    cbv_routes = [
        route
        for route in router.routes
        if isinstance(route, (Route, WebSocketRoute)) and route.endpoint in functions_set
    ]
    #dd(cbv_routes)

    # Now remove each route from the controller defined router
    # And ADD them into this new router
    for route in cbv_routes:
        #dd(route)
        router.routes.remove(route)
        _update_cbv_route_endpoint_signature(cls, route)
        cbv_router.routes.append(route)

    # Now add the routes BACK to the controller routes but this
    # time they have the customized route signature
    router.include_router(cbv_router)
    return cls


def _init_cbv(cls: Type[Any]) -> None:
    """
    Idempotently modifies the provided `cls`, performing the following modifications:
    * The `__init__` function is updated to set any class-annotated dependencies as instance attributes
    * The `__signature__` attribute is updated to indicate to FastAPI what arguments should be passed to the initializer
    """
    if getattr(cls, CBV_CLASS_KEY, False):  # pragma: no cover
        return  # Already initialized
    old_init: Callable[..., Any] = cls.__init__
    old_signature = inspect.signature(old_init)
    old_parameters = list(old_signature.parameters.values())[1:]  # drop `self` parameter
    new_parameters = [
        x for x in old_parameters if x.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    ]
    dependency_names: List[str] = []
    for name, hint in get_type_hints(cls).items():
        if is_classvar(hint):
            continue
        parameter_kwargs = {"default": getattr(cls, name, Ellipsis)}
        dependency_names.append(name)
        new_parameters.append(
            inspect.Parameter(name=name, kind=inspect.Parameter.KEYWORD_ONLY, annotation=hint, **parameter_kwargs)
        )
    new_signature = old_signature.replace(parameters=new_parameters)

    def new_init(self: Any, *args: Any, **kwargs: Any) -> None:
        for dep_name in dependency_names:
            dep_value = kwargs.pop(dep_name)
            setattr(self, dep_name, dep_value)
        old_init(self, *args, **kwargs)

    setattr(cls, "__signature__", new_signature)
    setattr(cls, "__init__", new_init)
    setattr(cls, CBV_CLASS_KEY, True)


def _update_cbv_route_endpoint_signature(cls: Type[Any], route: Union[Route, WebSocketRoute]) -> None:
    """
    Fixes the endpoint signature for a cbv route to ensure FastAPI performs dependency injection properly.
    """
    old_endpoint = route.endpoint
    #dd(old_endpoint)

    old_signature = inspect.signature(old_endpoint)
    #dd(old_signature)

    old_parameters: List[inspect.Parameter] = list(old_signature.parameters.values())
    #dd(old_parameters)

    old_first_parameter = old_parameters[0]
    new_first_parameter = old_first_parameter.replace(default=Depends(cls))
    new_parameters = [new_first_parameter] + [
        parameter.replace(kind=inspect.Parameter.KEYWORD_ONLY) for parameter in old_parameters[1:]
    ]
    # new_parameters = [
    #     parameter.replace(kind=inspect.Parameter.KEYWORD_ONLY) for parameter in old_parameters[1:]
    # ]
    #dd(new_parameters)
    new_signature = old_signature.replace(parameters=new_parameters)
    setattr(route.endpoint, "__signature__", new_signature)
