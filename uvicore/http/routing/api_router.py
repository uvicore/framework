from __future__ import annotations
import uvicore
from uvicore.typing import Any, Callable, List, Dict, Optional, Decorator, get_type_hints, Union, Type
from uvicore.http.routing.router import Router
from uvicore.contracts import ApiRoute as RouteInterface
from prettyprinter import pretty_call, register_pretty
from uvicore.support.dumper import dump, dd
from merge_args import _merge as merge_args
from functools import partial
from uvicore.http.response import Response, JSON as JSONResponse
from fastapi.datastructures import Default, DefaultPlaceholder


from uvicore.http.routing.guard import Guard
#from uvicore.auth.middleware.auth import Guard

# from fastapi import APIRouter as _FastAPIRouter
# from uvicore.typing import Any, Type, List, Callable, Optional
# from starlette.routing import BaseRoute
# from uvicore.contracts import ApiRouter as RouterInterface
# from starlette.responses import Response
# from uvicore.support.dumper import dump, dd
# from uvicore.support.module import load


@uvicore.service()
class ApiRouter(Router['ApiRoute']):

    def get(self,
        # Common to both ApiRouter and WebRouter
        path: str,
        endpoint: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        autoprefix: bool = True,
        middleware: Optional[List] = None,
        auth: Optional[Guard] = None,
        scopes: Optional[List] = None,
        inherits: Optional[Callable] = None,

        # ApiRouter specific
        responses: Optional[Dict] = None,
        response_model: Optional[Any] = None,
        response_class: Optional[Type[Response]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """Add a new HTTP GET route to the ApiRouter

        :param path: URL path, beginning with /
        :param endpoint: None if decorator, else method to call when route is fired.
        :param name: Name of this route to consistently access with url('name') helper.
        :param autoprefix: Disable the name autoprefixer (autoprefix adds the appname. prefix).  Useful when overriding another packages route.
        :param middleware: List of route level middleware.
        :param auth: Shorthand for the middleware=[Guard(['scope'])].  Usage auth=Guard(['scope']).
        :param scopes: Shorthand for middleware=[Guard(['scope'])].  Usage scopes=['scope1', 'scope1'].
        :param response_model: Response ORM Model.  Can also use -> Model on function return type.
        :param tags: List of tags to group the endpoint in the OpenAPI docs.
        :param summary: Summary of this endpoint for OpenAPI docs.
        :param description: Description of this endpoint for OpenAPI docs.
        :param inherits: Endpoint function can inhert the parameters of another function.  Useful if you have tons of parameters you want shared on multiple endpoints. Usage inherits=AuthApi.getsig.
        """
        # Build parameters
        methods = ['GET']
        #params = {key:value for key, value in locals().items() if key != 'self'}
        params = locals()
        params.pop('self')

        # Pass to generic add method
        return self.add(**params)

    def post(self,
        # Common to both ApiRouter and WebRouter
        path: str,
        endpoint: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        autoprefix: bool = True,
        middleware: Optional[List] = None,
        auth: Optional[Guard] = None,
        scopes: Optional[List] = None,
        inherits: Optional[Callable] = None,

        # ApiRouter specific
        responses: Optional[Dict] = None,
        response_model: Optional[Any] = None,
        response_class: Optional[Type[Response]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """Add a new HTTP POST route to the ApiRouter

        :param path: URL path, beginning with /
        :param endpoint: None if decorator, else method to call when route is fired.
        :param name: Name of this route to consistently access with url('name') helper.
        :param autoprefix: Disable the name autoprefixer (autoprefix adds the appname. prefix).  Useful when overriding another packages route.
        :param middleware: List of route level middleware.
        :param auth: Shorthand for the middleware=[Guard(['scope'])].  Usage auth=Guard(['scope']).
        :param scopes: Shorthand for middleware=[Guard(['scope'])].  Usage scopes=['scope1', 'scope1'].
        :param response_model: Response ORM Model.  Can also use -> Model on function return type.
        :param tags: List of tags to group the endpoint in the OpenAPI docs.
        :param summary: Summary of this endpoint for OpenAPI docs.
        :param description: Description of this endpoint for OpenAPI docs.
        :param inherits: Endpoint function can inhert the parameters of another function.  Useful if you have tons of parameters you want shared on multiple endpoints. Usage inherits=AuthApi.getsig.
        """
        # Build parameters
        methods = ['POST']
        #params = {key:value for key, value in locals().items() if key != 'self'}
        params = locals()
        params.pop('self')

        # Pass to generic add method
        return self.add(**params)

    def put(self,
        # Common to both ApiRouter and WebRouter
        path: str,
        endpoint: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        autoprefix: bool = True,
        middleware: Optional[List] = None,
        auth: Optional[Guard] = None,
        scopes: Optional[List] = None,
        inherits: Optional[Callable] = None,

        # ApiRouter specific
        responses: Optional[Dict] = None,
        response_model: Optional[Any] = None,
        response_class: Optional[Type[Response]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """Add a new HTTP PUT route to the ApiRouter

        :param path: URL path, beginning with /
        :param endpoint: None if decorator, else method to call when route is fired.
        :param name: Name of this route to consistently access with url('name') helper.
        :param autoprefix: Disable the name autoprefixer (autoprefix adds the appname. prefix).  Useful when overriding another packages route.
        :param middleware: List of route level middleware.
        :param auth: Shorthand for the middleware=[Guard(['scope'])].  Usage auth=Guard(['scope']).
        :param scopes: Shorthand for middleware=[Guard(['scope'])].  Usage scopes=['scope1', 'scope1'].
        :param response_model: Response ORM Model.  Can also use -> Model on function return type.
        :param tags: List of tags to group the endpoint in the OpenAPI docs.
        :param summary: Summary of this endpoint for OpenAPI docs.
        :param description: Description of this endpoint for OpenAPI docs.
        :param inherits: Endpoint function can inhert the parameters of another function.  Useful if you have tons of parameters you want shared on multiple endpoints. Usage inherits=AuthApi.getsig.
        """
        # Build parameters
        methods = ['PUT']
        #params = {key:value for key, value in locals().items() if key != 'self'}
        params = locals()
        params.pop('self')

        # Pass to generic add method
        return self.add(**params)

    def patch(self,
        # Common to both ApiRouter and WebRouter
        path: str,
        endpoint: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        autoprefix: bool = True,
        middleware: Optional[List] = None,
        auth: Optional[Guard] = None,
        scopes: Optional[List] = None,
        inherits: Optional[Callable] = None,

        # ApiRouter specific
        responses: Optional[Dict] = None,
        response_model: Optional[Any] = None,
        response_class: Optional[Type[Response]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """Add a new HTTP PATCH route to the ApiRouter

        :param path: URL path, beginning with /
        :param endpoint: None if decorator, else method to call when route is fired.
        :param name: Name of this route to consistently access with url('name') helper.
        :param autoprefix: Disable the name autoprefixer (autoprefix adds the appname. prefix).  Useful when overriding another packages route.
        :param middleware: List of route level middleware.
        :param auth: Shorthand for the middleware=[Guard(['scope'])].  Usage auth=Guard(['scope']).
        :param scopes: Shorthand for middleware=[Guard(['scope'])].  Usage scopes=['scope1', 'scope1'].
        :param response_model: Response ORM Model.  Can also use -> Model on function return type.
        :param tags: List of tags to group the endpoint in the OpenAPI docs.
        :param summary: Summary of this endpoint for OpenAPI docs.
        :param description: Description of this endpoint for OpenAPI docs.
        :param inherits: Endpoint function can inhert the parameters of another function.  Useful if you have tons of parameters you want shared on multiple endpoints. Usage inherits=AuthApi.getsig.
        """
        # Build parameters
        methods = ['PATCH']
        #params = {key:value for key, value in locals().items() if key != 'self'}
        params = locals()
        params.pop('self')

        # Pass to generic add method
        return self.add(**params)

    def delete(self,
        # Common to both ApiRouter and WebRouter
        path: str,
        endpoint: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        autoprefix: bool = True,
        middleware: Optional[List] = None,
        auth: Optional[Guard] = None,
        scopes: Optional[List] = None,
        inherits: Optional[Callable] = None,

        # ApiRouter specific
        responses: Optional[Dict] = None,
        response_model: Optional[Any] = None,
        response_class: Optional[Type[Response]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """Add a new HTTP DELETE route to the ApiRouter

        :param path: URL path, beginning with /
        :param endpoint: None if decorator, else method to call when route is fired.
        :param name: Name of this route to consistently access with url('name') helper.
        :param autoprefix: Disable the name autoprefixer (autoprefix adds the appname. prefix).  Useful when overriding another packages route.
        :param middleware: List of route level middleware.
        :param auth: Shorthand for the middleware=[Guard(['scope'])].  Usage auth=Guard(['scope']).
        :param scopes: Shorthand for middleware=[Guard(['scope'])].  Usage scopes=['scope1', 'scope1'].
        :param response_model: Response ORM Model.  Can also use -> Model on function return type.
        :param tags: List of tags to group the endpoint in the OpenAPI docs.
        :param summary: Summary of this endpoint for OpenAPI docs.
        :param description: Description of this endpoint for OpenAPI docs.
        :param inherits: Endpoint function can inhert the parameters of another function.  Useful if you have tons of parameters you want shared on multiple endpoints. Usage inherits=AuthApi.getsig.
        """
        # Build parameters
        methods = ['DELETE']
        #params = {key:value for key, value in locals().items() if key != 'self'}
        params = locals()
        params.pop('self')

        # Pass to generic add method
        return self.add(**params)

    def add(self,
        # Common to both ApiRouter and WebRouter
        path: str,
        endpoint: Optional[Callable] = None,
        methods: List[str] = ['GET'],
        *,
        name: Optional[str] = None,
        autoprefix: bool = True,
        middleware: Optional[List] = None,
        auth: Optional[Guard] = None,
        scopes: Optional[List] = None,
        inherits: Optional[Callable] = None,

        # ApiRouter specific
        responses: Optional[Dict] = None,
        response_model: Optional[Any] = None,
        response_class: Optional[Type[Response]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Callable[[Decorator], Decorator]:
        """Add a new HTTP method route to the ApiRouter

        :param path: URL path, beginning with /
        :param endpoint: None if decorator, else method to call when route is fired.
        :param name: Name of this route to consistently access with url('name') helper.
        :param autoprefix: Disable the name autoprefixer (autoprefix adds the appname. prefix).  Useful when overriding another packages route.
        :param middleware: List of route level middleware.
        :param auth: Shorthand for the middleware=[Guard(['scope'])].  Usage auth=Guard(['scope']).
        :param scopes: Shorthand for middleware=[Guard(['scope'])].  Usage scopes=['scope1', 'scope1'].
        :param response_model: Response ORM Model.  Can also use -> Model on function return type.
        :param tags: List of tags to group the endpoint in the OpenAPI docs.
        :param summary: Summary of this endpoint for OpenAPI docs.
        :param description: Description of this endpoint for OpenAPI docs.
        :param inherits: Endpoint function can inhert the parameters of another function.  Useful if you have tons of parameters you want shared on multiple endpoints. Usage inherits=AuthApi.getsig.
        """
        # Convert auth and scope helper param to middleware
        if middleware is None: middleware = []
        if auth: middleware.append(auth)
        if scopes: middleware.append(Guard(scopes))

        # Clean path and name
        (path, full_path, name, full_name) = self._format_path_name(path, name, autoprefix, methods)

        def handle(endpoint):
            nonlocal response_model
            nonlocal description

            # Merge function arguments if inheriting
            if inherits: endpoint = merge_args(inherits, endpoint)

            # If endpoint is partial, grab inside func for type hint and docstrings
            endpoint_func = endpoint
            if isinstance(endpoint, partial):
                # Endpoint is a partial (was overwritten to default some higher order middleware)
                # A partial overwrites the original docstring.  Functools update_wrapper will copy it back
                # as well as handle merging of other important properties
                #update_wrapper(route.endpoint, route.endpoint.func)
                endpoint_func = endpoint.func

                # Blank out the __doc__ on actual Partial itself, not actual endpoint inside partial.
                # If not, OpenAPI doc description will be partial(func, *args, **keywords) - new function with partial application etc...
                endpoint.__doc__ = None

            # Get response_model from typehint if not explicitly defined as a parameter
            response_model = response_model or get_type_hints(endpoint_func).get('return')

            # Get openapi description from route param or endpoint docstring
            description = description or endpoint_func.__doc__

            # Create route SuperDict
            route = ApiRoute({
                # Common to both ApiRouter and WebRouter
                'path': full_path,
                'name': full_name,
                'methods': methods,
                'endpoint': endpoint,
                'middleware': middleware,
                'autoprefix': autoprefix,
                'original_path': path,
                'original_name': name,
                'responses': responses,

                # ApiRouter specific
                'response_model': response_model,
                'response_class': response_class,
                'tags': tags,
                'summary': summary,
                'description': description,
            })
            # Full name already contains -POST, -PUT...for uniqueness across methods
            self.routes[full_name] = route
            return route

        # Method access
        if endpoint: return handle(endpoint)

        # Decorator access
        def decorator(func: Decorator) -> Decorator:
            handle(func)
            return func
        return decorator

@uvicore.service()
class ApiRoute(RouteInterface):
    """Route superdict definition"""
    pass


@register_pretty(ApiRoute)
def pretty_entity(value, ctx):
    """Custom pretty printer for my SuperDict"""
    # This printer removes the class name uvicore.types.Dict and makes it print
    # with a regular {.  This really cleans up the output!

    # SuperDict are printed as Dict, but this Package SuperDict should
    # be printed more like a class with key=value notation, so use **values
    return pretty_call(ctx, 'ApiRoute', **value)


# # Example of just using the entier FastAPI Router without abstraction
# @uvicore.service()
# class ApiRouter(_FastAPIRouter):

#     def resource(self, module, *, prefix: str = '', tags:List[str] = None) -> None:
#         """Include Controller Routes"""
#         if type(module) == str:
#             # Using a string to point to an endpoint class controller
#             module_path = module
#             if self.uvicore.endpoints: module_path = self.uvicore.endpoints + '.' + module_path
#             controller = load(module_path)
#             uvicore.app.http.include_router(
#                 controller.object,
#                 prefix=self.uvicore.prefix + str(prefix),
#                 tags=tags,
#             )
#         else:
#             # Passing in an actual router class
#             uvicore.app.http.include_router(
#                 module,
#                 prefix=self.uvicore.prefix + str(prefix),
#                 tags=tags,
#             )



# # @route.get('/about', 'about')
# # async def about(request: Request):
# #     # Example Jinja2 Template
# #     return response.View('wiki/about.j2', {'request': request})


# # Example of making my own router abstraction
# class ApiRouterX(RouterInterface):

#     @property
#     def router(self) -> _FastAPIRouter:
#         return self._router

#     # These properties have to exist because the FastAPI code looks for route.routes
#     # or routes.response_class for example so this router abstraction must pass them through
#     # Perhaps my own abstraction isn't a good idea?  Maybe just pass through fastAPI's router?
#     @property
#     def routes(self) -> List[BaseRoute]:
#         return self._router.routes

#     @property
#     def response_class(self) -> Type[Response]:
#         return self._router.response_class

#     @property
#     def default_response_class(self) -> Type[Response]:
#         return self._router.default_response_class

#     @property
#     def on_startup(self) -> None:
#         return self._router.on_startup

#     @property
#     def on_shutdown(self) -> None:
#         return self._router.on_shutdown

#     def __init__(self):
#         # Fireup FastAPI Router
#         self._router = _FastAPIRouter()

#     def get(self,
#         path: str,
#         name: str = None,
#         *,
#         response_model: Type[Any] = None,
#         include_in_schema: bool = True
#     ) -> Callable:
#         return self._router.get(
#             path=path,
#             name=name,
#             response_model=response_model,
#             include_in_schema=include_in_schema,
#         )

#     #def include_router(self, router: "APIRouter", *, prefix: str = '', tags: List[str] = None) -> None:
#     # def include_router(self, router: "APIRouter") -> None:
#     #     # Only used for the class based controller
#     #     # return self._router.include_router(router,
#     #     #     prefix=prefix,
#     #     #     tags=tags
#     #     # )
#     #     return self.router.include_router(router)

#     def add_api_route(self, path: str, endpoint: Callable, *,
#         response_model: Optional[Type[Any]] = None,
#         name: Optional[str] = None,
#         # self,
#         # path: str,
#         # endpoint: Callable,
#         # *,
#         # response_model: Optional[Type[Any]] = None,
#         # status_code: int = 200,
#         # tags: Optional[List[str]] = None,
#         # dependencies: Optional[Sequence[params.Depends]] = None,
#         # summary: Optional[str] = None,
#         # description: Optional[str] = None,
#         # response_description: str = "Successful Response",
#         # responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
#         # deprecated: Optional[bool] = None,
#         # methods: Optional[Union[Set[str], List[str]]] = None,
#         # operation_id: Optional[str] = None,
#         # response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
#         # response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
#         # response_model_by_alias: bool = True,
#         # response_model_exclude_unset: bool = False,
#         # response_model_exclude_defaults: bool = False,
#         # response_model_exclude_none: bool = False,
#         # include_in_schema: bool = True,
#         # response_class: Optional[Type[Response]] = None,
#         # name: Optional[str] = None,
#         # route_class_override: Optional[Type[APIRoute]] = None,
#         # callbacks: Optional[List[APIRoute]] = None,
#     ) -> None:
#         return self.router.add_api_route(
#             path=path,
#             endpoint=endpoint,
#             response_model=response_model,
#             name=name,
#             # status_code=status_code,
#             # tags=tags,
#             # dependencies=dependencies,
#             # summary=summary,
#             # description=description,
#             # response_description=response_description,
#             # responses=responses,
#             # deprecated=deprecated,
#             # methods=methods,
#             # operation_id=operation_id,
#             # response_model_include=response_model_include,
#             # response_model_exclude=response_model_exclude,
#             # response_model_by_alias=response_model_by_alias,
#             # response
#         )

#     # @property
#     # def router(self):
#     #     return self._router



# # IoC Class Instance
# #ApiRouter: RouterInterface = uvicore.ioc.make('ApiRouter', _ApiRouter)

# # Public API for import * and doc gens
# #__all__ = ['ApiRouter', '_ApiRouter']
