from __future__ import annotations
import uvicore
import inspect
from copy import copy
from functools import partial
from uvicore import contracts
from uvicore.support.module import load
from uvicore.support import str as string
from uvicore.support.dumper import dump, dd
from uvicore.http.routing.guard import Guard
from uvicore.support.dictionary import deep_merge
from uvicore.typing import Dict, Callable, List, TypeVar, Generic, Decorator, Optional

# Generic Route (Web or Api)
R = TypeVar('R')


@uvicore.service()
class Router(contracts.Router, Generic[R]):
    """Abstract base router class for Web and Api Router Implimentations"""

    @property
    def package(self) -> contracts.Package:
        return self._package

    @property
    def routes(self) -> Dict[str, R]:
        return self._routes

    def __init__(self, package: contracts.Package, prefix: str, name: str = '', controllers: str = None):
        # Instance variables
        self._package = package
        self._routes = Dict()
        self._tmp_routes = Dict()
        self.controllers: str = controllers

        # Prefix
        if prefix == '/': prefix = ''
        if prefix:
            if prefix[-1] == '/': prefix = prefix[0:-1]
            if prefix[0] != '/': prefix = '/' + prefix
        self.prefix = prefix

        # Clean name
        if name:
            name = name.replace('/', '.')
            if name[-1] == '.': name = name[0:-1]  # Remove trailing .
            if name[0] == '.': name = name[1:]     # Remove beginning .
        self.name = name

    def controller(self,
        module: Union[str, Callable],
        *,
        prefix: str = '',
        name: str = '',
        tags: Optional[List[str]] = None,
        options: Dict = {}
    ) -> List:
        if prefix:
            if prefix[-1] == '/': prefix = prefix[0:-1]  # Remove trailing /
            if prefix[0] != '/': prefix = '/' + prefix   # Add beginning /

        # Get name
        if not name: name = prefix

        # Clean name
        if name:
            name = name.replace('/', '.')
            if name[-1] == '.': name = name[0:-1]  # Remove trailing .
            if name[0] == '.': name = name[1:]     # Remove beginning .

        # Import controller module from string
        if type(module) == str:
            if self.controllers:
                if '.' not in module:
                    # We are defining just 'home', so we add .Home class
                    module = self.controllers + '.' + module + '.' + string.studly(module)
                elif module.count('.') == 1:
                    # We are defining the file and the class (home.Home)
                    module = self.controllers + '.' + module
                else:
                    # We are defining the FULL module path even though we have defined a self.controller path
                    pass
            module = load(module).object

        # Instantiate controller file
        controller: Routes = module(self.package, **options)

        # New self (Web or Api) router instance
        router = self.__class__(self.package, self.prefix + prefix, self.name + '.' + name, self.controllers)

        # Register controllers routes and return new updated router
        router = controller.register(router)

        # Add contoller class level attributes as middleware to each route on this controller
        controller_middlewares = controller._middleware()
        if controller_middlewares:
            for route in router.routes.values():
                (route.middleware, route.endpoint) = self._merge_route_middleware(controller_middlewares, route.middleware, route.endpoint)

        # Merge controllers routes into this main (parent of recursion) router
        #dump(router.routes)
        self.routes.merge(router.routes)

        # Return just this controllers routes as a list
        routes = []
        for route in router.routes.keys():
            routes.append(router.routes[route])

        return routes

    def include(self,
        module: Union[str, Callable],
        *,
        prefix: str = '',
        name: str = '',
        tags: Optional[List[str]] = None,
        options: Dict = {}
    ) -> List:
        """Alias to controller"""
        self.controller(module=module, prefix=prefix, name=name, tags=tags, options=options)

    def override(self, package_name: str, route_name: str, endpoint: Callable):
        # We have a package_name like mreschke.wiki
        # A route name like wiki.search
        # and a new endpoint callable
        # Find actual package, get that route, add to this packages routes but swap the callable
        # then when server is build, the MERGE of routes will take this one FIRST by name, so it overrides!
        pass

    def group(self, prefix: str = '', *,
        routes: Optional[List] = None,
        name: str = '',
        tags: Optional[List[str]] = None,
        autoprefix: bool = True,
        middleware: Optional[List] = None,
        auth: Optional[Guard] = None,
        scopes: Optional[List] = None,
    ) -> Callable[[Decorator], Decorator]:
        """Route groups method and decorator"""

        # Convert auth helper param to middleware
        if middleware is None: middleware = []
        if auth: middleware.append(auth)

        # Convert scopes to Guard route middleware
        if scopes:
            middleware.append(Guard(scopes))

        # Get name
        if not name: name = prefix

        # Clean name
        if name:
            name = name.replace('/', '.')
            if name[-1] == '.': name = name[0:-1]  # Remove trailing .
            if name[0] == '.': name = name[1:]     # Remove beginning .

        def handle(routes):
            # Controllers return multiple routes as a List, so flatten everything into one List
            all_routes = []
            for route in routes:
                if type(route) == list:
                    all_routes.extend(route)
                else:
                    all_routes.append(route)

            # New routes with updated prefixes
            new_routes = []

            # Loop group routes and update prefixes
            for route in all_routes:
                # Remove old route from self.routes
                if route.name in self.routes:
                    self.routes.pop(route.name)

                # Strip global prefix if exists
                path = route.path
                if len(path) >= len(self.prefix) and path[0:len(self.prefix)] == self.prefix:
                    path = path[len(self.prefix):]

                rname = route.name
                if len(rname) >= len(self.name) and rname[0:len(self.name)] == self.name:
                    rname = rname[len(self.name) + 1:]

                full_path = prefix + path
                full_name = name + '.' + rname

                # Get route middleware based on parent child overrides
                (route_middleware, route.endpoint) = self._merge_route_middleware(middleware, route.middleware, route.endpoint)
                #dump(route, middleware, route.middleware)

                # Add new route with new group prefix and name
                # Because this is a polymorphic router (works for Web and API router)
                # The self.add methods will be different.  The actual route should mimic the self.add
                # parameters, so modify the route when calculated values and pass in as
                # self.add **kwargs
                if tags:
                    if route.tags is None: route.tags = []
                    route.tags.extend(tags)
                route.path = full_path
                route.name = full_name
                route.autoprefix = autoprefix,
                route.middleware = route_middleware
                del route.original_path
                del route.original_name

                # NO, this didn't handle polymorphic router.  self.add is different for each router.
                # new_route = self.add(
                #     path=full_path,
                #     endpoint=route.endpoint,
                #     methods=route.methods,
                #     name=full_name,
                #     autoprefix=autoprefix,
                #     #middleware=route.middleware or middleware  # Closest one to the route wins
                #     middleware=route_middleware
                # )
                new_route = self.add(**route)
                new_routes.append(new_route)

            # Return new routes for recursive nested groups
            return new_routes

        # Method access
        if routes: return handle(routes)

        # Decorator access
        def decorator(func: Decorator) -> Decorator:
            # Backup and clear existing routes
            all_routes = self._routes.clone()
            self._routes = Dict()

            # Get routes from the group method
            func()

            # Build routes list from group method
            routes = []
            for route in self._routes.values():
                routes.append(route)

            # Restore all routes besides the ones in the gruop method
            self._routes = all_routes.clone()

            # Add these routes to the proper group
            handle(routes)
            return func

        return decorator

    def _merge_route_middleware(self, parent_middleware: List, child_middleware: List, endpoint: Callable) -> Tuple[List, Callable]:
        """Merge parent route middleware into child, children parameters win in merge.

        If endpoing method is middleware, merge that also and return a new partial endpoint
        """

        # Merge helper
        def merge(parent_middleware, child_middleware):
            # Get middleware __init__ params
            inspection = inspect.signature(parent_middleware.__init__)
            params = [x for x in inspection.parameters]

            # Build params key value Dict
            parent_params = Dict()
            child_params = Dict()
            for param in params:
                # If param value is None do NOT add to kwargs or even the None will win in a merge
                if getattr(parent_middleware, param) is not None:
                    parent_params[param] = getattr(parent_middleware, param)
                if getattr(child_middleware, param) is not None:
                    child_params[param] = getattr(child_middleware, param)

            # Deep merge params
            kwargs = deep_merge(child_params, parent_params, merge_lists=True)

            # Instantiate new middleware with new params
            # We can't just set child_middleware new dict values becuase it has already fired up
            # its super.__init__, so changing values now does nothing.  Instead we replace it with an all
            # new instantiated Guard
            new_middleware = parent_middleware.__class__(**kwargs)
            return new_middleware

        # New merged middleware
        middlewares = []

        # Both parent and child have middleware. If both have the same middleware,
        # create a new middleware based on a merge of parameters where CHILD params WIN.
        if parent_middleware and child_middleware:
            for child_middleware in child_middleware:
                found = False
                for parent_middleware in parent_middleware:
                    if str(parent_middleware) == str(child_middleware):
                        found = True
                        break

                if not found:
                    # No matching parent middleware, use child
                    middlewares.append(child_middleware)
                else:
                    # Found matching parent and child middleware.  Create new middleware with merged parameters of the two
                    # Because of the break statement, the current parent_middleware variable is the match
                    middlewares.append(merge(parent_middleware, child_middleware))

        elif parent_middleware:
            # We have parent middleware, no children
            middlewares = copy(parent_middleware)

        elif child_middleware:
            # We have child middleware, no parent
            middlewares = copy(child_middleware)

        # Check each endpoints params and look at its default value
        # Compare that default value to our list of middleware
        # If they are the same, REMOVE the middleware from our list
        # or we will trigger the same middleware twice.  Once in a group/controller
        # and once on the actual function parameter (with FastAPI Depends) as well.
        final_middleware = []
        if middlewares:
            # Get endpoing method signature end parameters
            endpoint_signature = inspect.signature(endpoint)
            endpoint_params = endpoint_signature.parameters

            # Loop all merged parent/child middleware
            for middleware in middlewares:
                add = True

                # Loop each endpoint parameter
                for endpoint_param in endpoint_params.values():
                    # Endpoint middleware will be the default value of a parameter
                    endpoint_middleware = endpoint_param.default

                    # Compare the endpoint default value with the current middleware
                    # If they are the same, this endpint parameter is middleware and matches
                    # on of our previously defined merged middlewares.
                    # If we find a match do NOT add current middleware to final_middleware to eliminate
                    # duplicate middleware being run twice.
                    if str(middleware) == str(endpoint_middleware):
                        # Do NOT add this middleware to final_middleware
                        add = False

                        # Merge endpoint middleware to higher level matched middleware
                        # This will merge scopes and other parameters to provide scope hierarchy
                        new_endpoint_middleware = merge(middleware, endpoint_middleware)

                        # Create a partial endpoint method with our new middleware parameter injected
                        # Partials see https://levelup.gitconnected.com/changing-pythons-original-behavior-8a43b7d1c55d
                        endpoint = partial(endpoint, **{
                            endpoint_param.name: new_endpoint_middleware
                        })

                        # There will not be another endpoint param matching this one middleware, break
                        break

                if add:
                    # No endpoint middleware found, add current middleware
                    final_middleware.append(middleware)

        # Return new merged middleware and modified partial endpoint
        return (final_middleware, endpoint)

    def _merge_route_middlewareOLD(self, parent_middleware: List, child_middleware: List) -> List:
        """Merge parent route middleware into child, children parameters win in merge."""

        # Parent has no middleware to merge into child
        if not parent_middleware: return child_middleware

        # if not child_middleware:
        #     # Child has no middleware of its own, add parent level middleware to this route
        #     return copy(parent_middleware)

        # Merge helper
        def merge(parent_middleware, child_middleware):
            # Get middleware __init__ params
            inspection = inspect.signature(parent_middleware.__init__)
            params = [x for x in inspection.parameters]

            # Build params key value Dict
            parent_params = Dict()
            child_params = Dict()
            for param in params:
                # If param value is None do NOT add to kwargs or even the None will win in a merge
                if getattr(parent_middleware, param) is not None:
                    parent_params[param] = getattr(parent_middleware, param)
                if getattr(child_middleware, param) is not None:
                    child_params[param] = getattr(child_middleware, param)

            # Deep merge params
            kwargs = deep_merge(child_params, parent_params, merge_lists=True)

            # Instantiate new middleware with new params
            # We can't just set child_middleware new dict values becuase it has already fired up
            # its super.__init__, so changing values now does nothing.  Instead we replace it with an all
            # new instantiated Guard
            new_middleware = parent_middleware.__class__(**kwargs)
            return new_middleware


        # Both parent and child have middleware. If both have the same middleware,
        # create a new middleware based on a merge of parameters where CHILD params WIN.
        middlewares = []
        if child_middleware:
            for child_middleware in child_middleware:
                found = False
                for parent_middleware in parent_middleware:
                    if str(parent_middleware) == str(child_middleware):
                        found = True
                        break

                if not found:
                    # No matching controller middleware found
                    middlewares.append(child_middleware)
                else:
                    # Found matching controller and route middleware.  Create new middleware with merged parameters of the two
                    # Because of the break, the current parent_middleware variable is the match
                    middlewares.append(merge(parent_middleware, child_middleware))
        else:
            middlewares = copy(parent_middleware)

        return middlewares

    def _clean_add(self, path: str, name: str, autoprefix: bool):
        # Clean path
        if path and path[-1] == '/': path = path[0:-1]  # Remove trailing /
        if path and path[0] != '/': path = '/' + path   # Add beginning /

        # Get name
        if not name: name = path

        # Clean name
        name = name.replace('/', '.')
        if name and name[-1] == '.': name = name[0:-1]  # Remove trailing .
        if name and name[0] == '.': name = name[1:]     # Remove beginning .
        if not name: name = 'root'

        # Autoprefix path and name
        # Note that route "name" is for URL linking
        # This does NOT use the global URL prefix because that can change by the user running the package
        # Instead we use the actual package name for the name prefix
        full_path = path
        full_name = name
        if autoprefix:
            full_path = self.prefix + full_path
            full_name = self.name + '.' + full_name
        return (path, full_path, name, full_name)


@uvicore.service()
class Routes(contracts.Routes):
    """Routes and Controller Class"""
    # middleware = None
    # auth = None
    # scopes = None

    @property
    def package(self) -> contracts.Package:
        return self._package

    def __init__(self, package: contracts.Package):
        self._package = package

    def _middleware(self):
        # Get class level middleware
        middlewares = []
        if self.auth: middlewares.append(self.auth)
        if self.middleware: middlewares.extend(self.middleware)
        if self.scopes: middlewares.append(Guard(self.scopes))

        return middlewares
        # if '__annotations__' in self.__class__.__dict__:
        #     for key, value in self.__class__.__annotations__.items():
        #         middlewares.append(getattr(self, key))
        # return middlewares


