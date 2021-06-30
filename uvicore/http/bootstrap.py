import uvicore
from uvicore.typing import Dict, List, OrderedDict, get_type_hints, Tuple
from uvicore.events import Handler
from uvicore.support import module
from uvicore.support.dumper import dump, dd
from uvicore.foundation.events.app import Booted as OnAppBooted
from uvicore.contracts import Package as Package
from uvicore.console import command_is
from starlette.applications import Starlette
from fastapi import FastAPI, Depends
from uvicore.http import response
from uvicore.http.events import server as HttpServerEvents
from uvicore.http.routing.router import Routes
from functools import partial, update_wrapper
from uvicore.http.routing import ApiRoute, WebRoute
from uvicore.http.routing import Guard
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html


class Http(Handler):

    def __call__(self, event: OnAppBooted):
        """Bootstrap the HTTP Server after the Application is Booted"""

        # This will never fire if the uvicore.http module is not loaded
        # This will fire even if in console mode so we can handle showing routes
        # on certain commands.

        # Import each packages router files and add their routes to the package definition
        self.build_package_routes()

        # Fire up the HTTP server only if running from HTTP
        # Notice this is below building package routes above.  This is because
        # package routes are still built with certain CLI groups like package list and http route.
        # The server however is NOT fired up if not running a full http server command
        if not uvicore.app.is_http: return

        # Merge all packages Web and Api routes
        (web_routes, api_routes) = self.merge_routes()

        # If no routes, do nothing, no HTTP server at all
        if not web_routes and not api_routes: return

        # Fire up one or multiple HTTP servers.
        # If we have both web and api routes then we will mount subservers.
        # If not, we will only use one server.
        (base_server, web_server, api_server) = self.create_http_servers(web_routes, api_routes)

        # Add global web and api specific middleware
        self.add_middleware(web_server, api_server)

        # Get configured web and api prefixes
        web_prefix = self.get_prefix('app.web.prefix')
        api_prefix = self.get_prefix('app.api.prefix')

        # Add web routes to the web server
        self.add_web_routes(web_server, web_routes, web_prefix if not base_server else '')

        # Add api routes to the api server
        self.add_api_routes(api_server, api_routes, api_prefix if not base_server else '')

        # Add web paths (public, asset, view) and configure templates
        self.configure_webserver(web_server)

        # Fire up the proper servers and set our global app.http instance
        if base_server:
            # Running both web and api servers, we must have a perent base server
            # to mount the web and api sub servers into.  This is how we properly
            # separate web vs api middleware and other configurations.
            # Longer prefix has to be FIRST to match subapp regex properly
            if len(web_prefix) > len(api_prefix):
                base_server.mount(web_prefix, web_server)  # Web first
                base_server.mount(api_prefix, api_server)
            else:
                base_server.mount(api_prefix, api_server)  # Api first
                base_server.mount(web_prefix, web_server)
            uvicore.app._http = base_server
        elif web_server:
            # We only have a web server (no api routes)
            uvicore.app._http = web_server
        elif api_server:
            # We only have an api server (no web routes)
            uvicore.app._http = api_server

        # Attach to Starlette events and translate into Uvicore events
        @uvicore.app.http.on_event("startup")
        async def startup():
            await HttpServerEvents.Startup().dispatch_async()

        @uvicore.app.http.on_event("shutdown")
        async def shutdown():
            await HttpServerEvents.Shutdown().dispatch_async()


        # # Experiment add custom exceptions
        # When you do, see if you can get JSON responses to api_server and HTML responses to web_server
        # And adjust the JSON from fastapi exception_handler.py to {message} not {detail} to look more like kongs return
        # async def internal_server_error_500(request, exc):
        #     print(exc)
        #     return response.HTML(content='custom 500 internal server error', status_code=500)

        # async def not_found_404(request, exc):
        #     print(exc)
        #     return response.HTML(content='custom 404 not found', status_code=505)
        # uvicore.app.http.server.add_exception_handler(500, internal_server_error_500)
        # uvicore.app.http.server.add_exception_handler(404, not_found_404)
        # #dump('xxxxxx', uvicore.app.http.server.exception_handlers)


        # Debug and dump the actual HTTP servers (base, web, api) info and routes
        debug_dump = False
        if debug_dump:
            dump('#################################################################')
            dump("Main HTTP Server APPLICATION", uvicore.app.http.__dict__)

            dump('#################################################################')
            dump("Main HTTP Server Routes")
            for route in uvicore.app.http.routes:
                dump(route.__dict__)

            for route in uvicore.app.http.routes:
                if route.name is None:
                    dump('#################################################################')
                    dump("Sub Server '{}' APPLICATION".format(route.path))
                    dump(route.app.__dict__)

                    dump('#################################################################')
                    dump("Sub Server '{}' Routes".format(route.path))
                    for r in route.app.router.routes:
                        dump(r.__dict__)

    def build_package_routes(self) -> None:
        """Import all packages web and api routes files and add to packages route definition"""
        for package in uvicore.app.packages.values():
            if package.web.routes_module or package.api.routes_module:
                package.web.routes = self.import_package_web_routes(package)
                package.api.routes = self.import_package_api_routes(package)

    def import_package_web_routes(self, package: Package) -> Dict:
        """Import one package web routes and return routes Dict"""

        # If no routes_modules defined, nothing todo
        if not package.web.routes_module: return

        # Allow only if running as HTTP or from certain CLI commands like package list/show...
        if package.registers.web_routes and (
            uvicore.app.is_http or
            command_is('http') or
            command_is('package') or
            command_is('ioc')
        ) == False: return

        routes_module = package.web.routes_module
        prefix = package.web.prefix
        name_prefix = package.web.name_prefix

        # Import main web routes module
        routes: Routes = module.load(routes_module).object(package)

        # Get name prefix from package name plus custom name prefix
        if name_prefix:
            if name_prefix[0] == '.': name_prefix = name_prefix[1:]
            name_prefix = package.short_name + '.' + name_prefix
        else:
            name_prefix = package.short_name

        # Import the web router and create a new instance
        from uvicore.http.routing.web_router import WebRouter  # isort:skip
        router = WebRouter(package, prefix, name_prefix)

        # Get returned router with all defined routes
        router = routes.register(router)

        # Merge routes level middleware into each route
        routes_middleware = routes._middleware()
        if routes_middleware:
            for route in router.routes.values():
                (route.middleware, route.endpoint) = router._merge_route_middleware(routes_middleware, route.middleware, route.endpoint)

        # Return routes
        return router.routes

    def import_package_api_routes(self,  package: Package) -> Dict:
        """Import one package api routes and return routes Dict"""

        # If no routes_modules defined, nothing todo
        if not package.api.routes_module: return

        # Allow only if running as HTTP or from certain CLI commands like package list/show...
        if package.registers.api_routes and (
            uvicore.app.is_http or
            command_is('http') or
            command_is('package') or
            command_is('ioc')
        ) == False: return

        routes_module = package.api.routes_module
        prefix = package.api.prefix
        name_prefix = package.api.name_prefix

        # Import main web routes module
        routes: Routes = module.load(routes_module).object(package)

        # Get name prefix from package name plus custom name prefix
        if name_prefix:
            if name_prefix[0] == '.': name_prefix = name_prefix[1:]
            name_prefix = package.short_name + '.' + name_prefix
        else:
            name_prefix = package.short_name

        # Import the api router and create a new instance
        from uvicore.http.routing.api_router import ApiRouter  # isort:skip
        router = ApiRouter(package, prefix, name_prefix)

        # Get returned router with all defined routes
        router = routes.register(router)

        # Merge routes level middleware into each route
        routes_middleware = routes._middleware()
        if routes_middleware:
            for route in router.routes.values():
                (route.middleware, route.endpoint) = router._merge_route_middleware(routes_middleware, route.middleware, route.endpoint)

        #Return routes
        return router.routes

    def merge_routes(self) -> Tuple[Dict[str, WebRoute], Dict[str, ApiRoute]]:
        """Merge all packages web and api routes together"""
        web_routes = Dict()
        api_routes = Dict()
        for package in uvicore.app.packages.values():
            # Merging in package order ensures last package wins!
            if package.web.routes:
               web_routes.merge(package.web.routes)
            if package.api.routes:
                api_routes.merge(package.api.routes)
        return (web_routes, api_routes)

    def create_http_servers(self, web_routes: Dict[str, WebRoute], api_routes: Dict[str, ApiRoute]) -> Tuple[Starlette, FastAPI, FastAPI]:
        """Fire up one or multiple HTTP servers"""

        # If we have both web and api routes then we will submount subservers.
        # If not, we will only use one server.
        base_server: Starlette = None
        web_server: FastAPI = None
        api_server: FastAPI = None
        debug = uvicore.config('app.debug'),

        # Base server is Starlette
        if web_routes and api_routes:
            base_server = Starlette(
                debug=debug,
            )

        # Web server is FastAPI with NO OpenAPI setup
        if web_routes:
            web_server = FastAPI(
                debug=debug,
                version=uvicore.app.version,
                openapi_url=None,
                swagger_ui_oauth2_redirect_url=None,
            )

        # Api server is FastAPI with OpenAPI setup
        if api_routes:
            api_server = FastAPI(
                debug=debug,
                #title=uvicore.config('app.api.openapi.title'),
                version=uvicore.app.version,
                #openapi_url=uvicore.config('app.api.openapi.url'),
                #swagger_ui_oauth2_redirect_url=uvicore.config('app.api.openapi.docs_url') + '/oauth2-redirect',

                # Default FastAPI docs and redoc routes
                #docs_url=uvicore.config('app.api.openapi.docs_url'),
                #redoc_url=uvicore.config('app.api.openapi.redoc_url'),

                docs_url=None,
                redoc_url=None,

                #swagger_ui_oauth2_redirect_url=


                #root_path='/api',  #fixme with trying out kong
            )
        return (base_server, web_server, api_server)

    def add_middleware(self, web_server: FastAPI, api_server: FastAPI) -> None:
        """Add global web and api middleware to their respective servers"""

        # Add global web middleware
        if web_server:
            for name, middleware in uvicore.config.app.web.middleware.items():
                cls = module.load(middleware.module).object
                web_server.add_middleware(cls, **middleware.options)

        # Add global api middleware
        if api_server:
            for name, middleware in uvicore.config.app.api.middleware.items():
                cls = module.load(middleware.module).object
                api_server.add_middleware(cls, **middleware.options)

    def add_web_routes(self, web_server, web_routes: Dict[str, WebRoute], prefix) -> None:
        """Add web routes to the web server"""
        for route in web_routes.values():
            web_server.add_api_route(
                path=(prefix + route.path) or '/',
                endpoint=route.endpoint,
                methods=route.methods,
                name=route.name,
                include_in_schema=False,
                response_class=response.HTML,
                dependencies=route.middleware,
            )
            # Starlette
            # web_server.add_route(
            #     path=route.path,
            #     route=route.endpoint,
            #     methods=route.methods,
            #     name=route.name,
            # )

    def add_api_routes(self, api_server, api_routes: Dict[str, ApiRoute], prefix) -> None:
        """Add api routes to the api server"""

        # Get important app configs
        api_prefix = uvicore.config.app.api.prefix  # Different that the prefix parameter
        openapi = uvicore.config.app.api.openapi
        oauth2 = uvicore.config.app.auth.oauth2

        # Determine if OpenAPI docs oauth2 authentication is enabled
        # If OpenAPI oauth2 is enabled, create a FastAPI OAuth2AuthorizationCodeBearer variable
        if openapi.oauth2_enabled and oauth2:
            from fastapi.security import OAuth2AuthorizationCodeBearer
            oauth2_scheme = OAuth2AuthorizationCodeBearer(
                authorizationUrl=oauth2.base_url + oauth2.authorize_path,
                tokenUrl=oauth2.base_url + oauth2.token_path,
            )

        # Create our own custom OpenAPI docs route
        if openapi.path and openapi.docs.path:

            # Oauth2 redirect URL (without api_prefid)
            openapi_redirect_url =  openapi.docs.path + '/login'

            @api_server.get(openapi.docs.path, include_in_schema=False)
            def openapi_docs():
                return get_swagger_ui_html(
                    openapi_url=api_prefix + openapi.path,
                    title=openapi.title,

                    swagger_favicon_url=openapi.docs.favicon_url,
                    swagger_js_url=openapi.docs.js_url,
                    swagger_css_url=openapi.docs.css_url,
                    oauth2_redirect_url=api_prefix + openapi_redirect_url,
                    init_oauth={
                        'clientId': oauth2.client_id,
                        #'clientSecret': "GaMz_F83_KB8ac6g-Eds0uoHyeoxg03X184yBqZR5Ws",
                        #'realm': "https://auth-local.triglobal.io",
                        'appName': uvicore.config.app.name,
                        #'scopeSeparator': " ",
                        'scopes': "openid profile",
                        #'additionalQueryStringParams': {'client_id': "7cc7d2a5-cc02-43ca-93bc-8476370ebf9d"},
                        #'usePkceWithAuthorizationCodeGrant': False
                    },
                )

            @api_server.get(openapi_redirect_url, include_in_schema=False)
            def openapi_redirect():
                return get_swagger_ui_oauth2_redirect_html()


        # Loop each uvicore route and add as FastAPI route
        for route in api_routes.values():
            endpoint_func = route.endpoint
            response_model = route.response_model

            # If endpoint is partial, grab inside func for type hindint and docstrings
            if isinstance(route.endpoint, partial):
                # Endpoint is a partial (was overwritten to default some higher order middleware)
                # A partial overwrites the original docstring.  Functools update_wrapper will copy it back
                # as well as handle merging of other important properties
                #update_wrapper(route.endpoint, route.endpoint.func)
                endpoint_func = route.endpoint.func

                # Blank out the __doc__ on actual Partial itself, not actual endpoint inside partial.
                # If not, OpenAPI doc description will be partial(func, *args, **keywords) - new function with partial application etc...
                route.endpoint.__doc__ = None

            # Get response model from parameter or infer from endpoint return type hint
            #response_model = route.response_model if route.response_model else get_type_hints(endpoint_func).get('return')
            response_model = route.response_model or get_type_hints(endpoint_func).get('return')

            # Get openapi description from route param or endpoint docstring
            description = route.description or endpoint_func.__doc__

            # If OpenAPI oauth2 authentication is enabled, add the proper route
            # dependency to our oauth2_schema
            if openapi.oauth2_enabled:
                found_guard = False
                for middleware in route.middleware:
                    if type(middleware) == Guard:
                        found_guard = True
                        break;

                if found_guard:
                    route.middleware.append(Depends(oauth2_scheme))


            # Add uvicore route to FastAPI route
            api_server.add_api_route(
                path=(prefix + route.path) or '/',
                endpoint=route.endpoint,
                methods=route.methods,
                name=route.name,
                response_model=response_model,
                tags=route.tags,
                dependencies=route.middleware,
                summary=route.summary,
                description=description,
            )

    def configure_webserver(self, web_server) -> None:
        """Configure the webserver with public, asset and view paths and template options"""

        # Ignore if web_server was never fired up
        if not web_server: return

        # Loop each package with an HTTP definition and add to our HTTP server
        public_paths = []
        asset_paths = []
        view_paths = []
        template_options = Dict()
        for package in uvicore.app.packages.values():
            #if not 'http' in package: continue
            if not 'web' in package: continue

            # Append public paths for later
            for path in package.web.public_paths:
                path_location = module.location(path)
                if path_location not in public_paths: public_paths.append(path_location)

            # Append asset paths for later
            for path in package.web.asset_paths:
                path_location = module.location(path)
                if path_location not in asset_paths: asset_paths.append(path_location)

            # Append template paths
            for path in package.web.view_paths or []:
                view_paths.append(path)

            # Deep merge template options
            template_options.merge(package.web.template_options or {})

        # Mount all static paths
        self.mount_static(web_server, public_paths, asset_paths)

        # Initialize new template environment from the options above
        self.initialize_templates(view_paths, template_options)

    def mount_static(self, web_server, public_paths: List, asset_paths: List) -> None:
        """Mount static routes defined in all packages"""
        StaticFiles = uvicore.ioc.make('uvicore.http.static.StaticFiles')

        # Mount all asset paths
        # Last directory defined WINS, which fits our last provider wins
        asset_url = uvicore.config.app.web.asset.path or '/assets'
        web_server.mount(asset_url, StaticFiles(directories=asset_paths), name='assets')

        # Mount all public paths (always at /)
        # Since it is root / MUST be defined last or it wins above any path after it
        web_server.mount('/', StaticFiles(directories=public_paths), name='public')

    def initialize_templates(self, paths, options) -> None:
        """Initialize and configure template system"""
        # Get the template singleton from the IoC
        templates = uvicore.ioc.make('uvicore.http.templating.jinja.Jinja')

        # Add all packages view paths
        for path in paths:
            templates.include_path(module.location(path))

        # Add all packages deep_merged template options
        if 'context_functions' in options:
            for name, method in options['context_functions'].items():
                templates.include_context_function(name, method)
        if 'context_filters' in options:
            for name, method in options['context_filters'].items():
                templates.include_context_filter(name, method)
        if 'filters' in options:
            for name, method in options['filters'].items():
                templates.include_filter(name, method)
        if 'tests' in options:
            for name, method in options['tests'].items():
                templates.include_test(name, method)

        # Initialize template system
        templates.init()

    def get_prefix(self, confpath: str) -> str:
        """Get configured web and api prefixes ensuring "" prefix and no trailing /, or / if blank)"""
        prefix = uvicore.config(confpath)
        #if not prefix: prefix = '/'
        #if prefix != '/' and prefix[-1] == '/': prefix = prefix[0:-1]  # No trailing /
        if prefix and prefix[-1] == '/': prefix = prefix[0:-1]  # No trailing /
        return prefix
