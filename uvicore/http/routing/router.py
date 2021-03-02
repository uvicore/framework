from __future__ import annotations
import uvicore
import inspect
from uvicore import contracts
from uvicore.typing import Dict, Callable, List, TypeVar, Generic, Decorator
from uvicore.support.dumper import dump, dd
from uvicore.support import str as string
from uvicore.support.module import load
from uvicore.support.dictionary import deep_merge
from copy import copy

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

    def controller(self, module: Union[str, Callable], *, prefix: str = '', name: str = ''):
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

        # Instantiate Controller
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

        # fixme, if string import it...
        controller = module(self.package)

        # New self (Web or Api) router instance
        router = self.__class__(self.package, self.prefix + prefix, self.name + '.' + name, self.controllers)

        # Register controllers routes and return new updated router
        router = controller.register(router)

        # Add contoller class level attributes as middleware to each route on this controller
        controller_middlewares = controller.middleware()
        if controller_middlewares:
            for route in router.routes.values():
                route.middleware = self._merge_route_middleware(controller_middlewares, route.middleware)

        # Merge controllers routes into this main (parent of recursion) router
        #dump(router.routes)
        self.routes.merge(router.routes)

        # Return just this controllers routes as a list
        routes = []
        for route in router.routes.keys():
            routes.append(router.routes[route])

        return routes

    def include(self, module, *, prefix: str = '', name: str = ''):
        """Alias to controller"""
        self.controller(module=module, prefix=prefix, name=name)

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
        autoprefix: bool = True,
        middleware: List = [],
        auth: Optional[Guard] = None,
    ):
        # Other params per group might be:
        # response_class, include_in_schame, tags, dependencies, maybe response_model??
        # Detect decorator
        #if not routes:
            #dd('decorat')

        # Convert auth helper param to middleware
        if auth: middleware.append(auth)

        def handle(routes):
            nonlocal prefix, name, autoprefix
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

                # Get name
                if not name: name = prefix

                # Clean name
                if name:
                    name = name.replace('/', '.')
                    if name[-1] == '.': name = name[0:-1]  # Remove trailing .
                    if name[0] == '.': name = name[1:]     # Remove beginning .

                # Get full paths
                full_path = prefix + route.original_path
                full_name = name + '.' + route.original_name


                # Strip global prefix if exists
                path = route.path
                if len(path) > len(self.prefix) and path[0:len(self.prefix)] == self.prefix:
                    path = path[len(self.prefix):]

                rname = route.name
                if len(rname) > len(self.name) and rname[0:len(self.name)] == self.name:
                    rname = rname[len(self.name) + 1:]

                full_path = prefix + path
                full_name = name + '.' + rname


                # Get route middleware based on parent child overrides
                route_middleware = self._merge_route_middleware(middleware, route.middleware)

                # Add new route with new group prefix and name
                new_route = self.add(
                    path=full_path,
                    endpoint=route.endpoint,
                    methods=route.methods,
                    name=full_name,
                    autoprefix=autoprefix,
                    #middleware=route.middleware or middleware  # Closest one to the route wins
                    middleware=route_middleware
                )
                new_routes.append(new_route)

            # Return new routes for recursive nested groups
            return new_routes

       # Method access
        if routes: return handle(routes)

        # Decorator access
        def decorator(func):
            # Backup and clear existing routes
            all_routes = self._routes.copy()
            self._routes = Dict()

            # Get routes from the group method
            func()

            # Build routes list from group method
            routes = []
            for route in self._routes.values():
                routes.append(route)

            # Restore all routes besides the ones in the gruop method
            self._routes = all_routes.copy()

            # Add these routes to the proper group
            handle(routes)
            return func
        return decorator

    def _merge_route_middleware(self, parent_middleware: List, child_middleware: List):
        """Merge parent route middleware into child, children parameters win in merge."""

        # Parent has no middleware to merge into child
        if not parent_middleware: return child_middleware

        if not child_middleware:
            # Child has no middleware of its own, add parent level middleware to this route
            return copy(parent_middleware)

        # Both parent and child have middleware. If both have the same middleware,
        # create a new middleware based on a merge of parameters where CHILD params WIN.
        middleware = []
        for child_middleware in child_middleware:
            found = False
            for parent_middleware in parent_middleware:
                if str(parent_middleware) == str(child_middleware):
                    found = True
                    break

            if not found:
                # No matching controller middleware found
                middleware.append(child_middleware)
            else:
                # Found matching controller and route middleware.  Create new middleware with merged parameters of the two
                # Because of the break, the current parent_middleware variable is the match

                # Get middleware __init__ params
                inspection = inspect.signature(parent_middleware.__init__)
                params = [x for x in inspection.parameters]

                # Build params key value Dict
                controller_params = Dict()
                route_params = Dict()
                for param in params:
                    # If param value is None do NOT add to kwargs or even the None will win in a merge
                    if getattr(parent_middleware, param) is not None:
                        controller_params[param] = getattr(parent_middleware, param)
                    if getattr(child_middleware, param) is not None:
                        route_params[param] = getattr(child_middleware, param)

                # Deep merge params
                kwargs = deep_merge(route_params, controller_params, merge_lists=True)

                # Instantiate new middleware with new params
                new_middleware = parent_middleware.__class__(**kwargs)

                # Add new middleware
                middleware.append(new_middleware)

        # Return new merged middleware
        return middleware



    def _clean_add(self, path: str, name: str, autoprefix: bool):
        # Clean path
        if path and path[-1] == '/': path = path[0:-1]  # Remove trailing /
        if path and path[0] != '/': path = '/' + path   # Add beginning /

        # Get name
        if not name: name = path

        # Clean name
        name = name.replace('/', '.')
        if name[-1] == '.': name = name[0:-1]  # Remove trailing .
        if name[0] == '.': name = name[1:]     # Remove beginning .

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

    @property
    def package(self) -> contracts.Package:
        return self._package

    def __init__(self, package: contracts.Package):
        self._package = package

    def middleware(self):
        # Get class level attributes as route middleware
        middlewares = []
        if '__annotations__' in self.__class__.__dict__:
            for key, value in self.__class__.__annotations__.items():
                middlewares.append(getattr(self, key))
        return middlewares


