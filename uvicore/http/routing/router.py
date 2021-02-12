from __future__ import annotations
import uvicore
from uvicore import contracts
from uvicore.typing import Dict, Callable, List, TypeVar, Generic
from uvicore.support.dumper import dump, dd

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

    def __init__(self, package: contracts.Package, prefix: str, name: str = ''):
        # Instance variables
        self._package = package
        self._routes = Dict()

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


    def controller(self, module, *, prefix: str = '', name: str = ''):
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
        # fixme, if string import it...
        controller = module(self.package)

        # New self (Web or Api) router instance
        router = self.__class__(self.package, self.prefix + prefix, self.name + '.' + name)

        # Register controllers routes and return new updated router
        router = controller.register(router)

        # Merge controllers routes into this main (parent of recursion) router
        self.routes.merge(router.routes)

        # Return just this controllers routes as a list
        routes = []
        for route in router.routes.keys():
            routes.append(router.routes[route])

        return routes

    def override(self, package_name: str, route_name: str, endpoint: Callable):
        # We have a package_name like mreschke.wiki
        # A route name like wiki.search
        # and a new endpoint callable
        # Find actual package, get that route, add to this packages routes but swap the callable
        # then when server is build, the MERGE of routes will take this one FIRST by name, so it overrides!
        pass

    def group(self, prefix: str = '', *, routes: Optional[List] = None, name: str = '', autoprefix: bool = True):
        # Other params per group might be:
        # response_class, include_in_schame, tags, dependencies, maybe response_model??
        # Detect decorator
        if not routes:
            dd('decorat')

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



            #dd(route, full_path, full_name, name)

            # Add new route with new group prefix and name
            new_route = self.add(
                path=full_path,
                endpoint=route.endpoint,
                methods=route.methods,
                name=full_name,
                autoprefix=autoprefix,
            )
            new_routes.append(new_route)

        # Return new routes for recursive nested groups
        return new_routes

    def _clean_add(self, path: str, name: str, autoprefix: bool):
        # Clean path
        if path[-1] == '/': path = path[0:-1]  # Remove trailing /
        if path[0] != '/': path = '/' + path   # Add beginning /

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


