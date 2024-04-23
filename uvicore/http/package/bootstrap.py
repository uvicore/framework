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
from uvicore.http.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from uvicore.http.rapidoc.docs import get_rapidoc_ui_html, get_rapidoc_pdf_ui_html, get_rapidoc_ui_oauth2_redirect_html

# Temp speed testing variable to swap Web router from FastAPI to Starlette
# NOTICE if you set this to TRUE, all your type hinded /{vars} and ?vars will NOT
# work in your routes and you will have to revert to Starlettes way of
# handling vars with request.path_params['user_id'] which will break all your apps.
USE_STARLETTE=False


class Http(Handler):

    def __call__(self, event: OnAppBooted):
        """Bootstrap the HTTP Server after the Application is Booted"""

        # This will never fire if the uvicore.http module is not loaded
        # This will fire even if in console mode so we can handle showing routes
        # on certain commands.

        # Import each packages router files and add their routes to the package definition
        self.build_package_routes()

        # Merge all packages Web and Api routes
        (web_routes, api_routes) = self.merge_routes()

        # Fire up the HTTP server only if running from HTTP
        # Notice this is below building package routes above.  This is because
        # package routes are still built with certain CLI groups like package list and http route.
        # The server however is NOT fired up if not running a full http server command
        if not uvicore.app.is_http: return

        # If no routes, do nothing, no HTTP server at all
        if not web_routes and not api_routes: return

        # Fire up one or multiple HTTP servers.
        # If we have both web and api routes then we will mount subservers.
        # If not, we will only use one server.
        (base_server, web_server, api_server) = self.create_http_servers(web_routes, api_routes)

        #dd("Base: ", base_server, "WEB: ", web_server, "API: ", api_server)

        # Add global web and api specific middleware
        self.add_middleware(web_server, api_server)

        # Add global web and api specific exception handlers
        self.add_exception_handlers(web_server, api_server)

        # Get configured web and api prefixes
        web_prefix = self.get_prefix('app.web.prefix')
        api_prefix = self.get_prefix('app.api.prefix')

        # Add web routes to the web server
        self.add_web_routes(web_server, web_routes)

        # Add api routes to the api server
        self.add_api_routes(api_server, api_routes)

        # Add web paths (public, asset, view), configure templates and view composers
        self.configure_webserver(web_server)

        # Mount our sub servers into our base server
        if web_server and api_server:
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
        elif web_server:
            base_server.mount(web_prefix, web_server)
        elif api_server:
            base_server.mount(api_prefix, api_server)

        # Add our base server to uvicore
        uvicore.app._http = base_server


        # Attach to Starlette events and translate into Uvicore events
        @uvicore.app.http.on_event("startup")
        async def startup():
            await HttpServerEvents.Startup().dispatch_async()

        @uvicore.app.http.on_event("shutdown")
        async def shutdown():
            await HttpServerEvents.Shutdown().dispatch_async()

        # Debug and dump the actual HTTP servers (base, web, api) info and routes
        debug_dump = False
        if debug_dump:
            dump("Base: ", base_server, "WEB: ", web_server, "API: ", api_server)

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
            command_is('ioc') or
            command_is('app')
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

        # Add to application running config for debug overview only
        uvicore.app.add_running_config('http.web.route_modules.[' + routes_module + '].prefix', prefix)
        uvicore.app.add_running_config('http.web.route_modules.[' + routes_module + '].name_prefix', name_prefix)

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
            command_is('ioc') or
            command_is('app')
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

        # Add to application running config for debug overview only
        uvicore.app.add_running_config('http.api.route_modules.[' + routes_module + '].prefix', prefix)
        uvicore.app.add_running_config('http.api.route_modules.[' + routes_module + '].name_prefix', name_prefix)

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

        # This merging means we can overwrite other packages routes.
        # Last package define wins in a route override battle
        web_routes = Dict()
        api_routes = Dict()
        package: Package
        for package in uvicore.app.packages.values():
            # Merging in package order ensures last package wins!
            if package.web.routes and package.registers.web_routes:
               web_routes.merge(package.web.routes)
            if package.api.routes and package.registers.api_routes:
                api_routes.merge(package.api.routes)

        # Add to application running config for debug overview only
        uvicore.app.add_running_config('http.web.routes', web_routes)
        uvicore.app.add_running_config('http.api.routes', api_routes)

        # Return routes tuple
        return (web_routes, api_routes)

    def create_http_servers(self, web_routes: Dict[str, WebRoute], api_routes: Dict[str, ApiRoute]) -> Tuple[Starlette, FastAPI, FastAPI]:
        """Fire up one or multiple HTTP servers"""

        # If we have both web and api routes then we will submount subservers.
        # If not, we will only use one server.
        base_server: Starlette = None
        web_server: FastAPI = None
        api_server: FastAPI = None
        debug = uvicore.config('app.debug')

        # We ALWAYS have 2 servers and the base_server (parent) is alway starlette
        # Why 2 servers?  Because of our web and api prefixes.  The web and api servers
        # get "mounted" inside the base wtih a special prefix to separate all routes and api docs

        # Base server is always starlette
        base_server = Starlette(debug=debug)

        # Web server is always a sub Starlette server
        if web_routes:
            if USE_STARLETTE:
                web_server = Starlette(debug=debug)
            else:
                web_server = FastAPI(
                    debug=debug,
                    version=uvicore.app.version,
                    openapi_url=None,
                    swagger_ui_oauth2_redirect_url=None,
                )

        # API server is always a sub FastAPI server
        if api_routes:
            api_server = FastAPI(
                debug=debug,

                #openapi_prefix=api_prefix,
                #root_path=api_prefix,
                #openapi_url='/api/openapi.json',

                #docs_url='/api/docs',
                #redoc_url='/api/`redoc`',

                # This title is what shows up in OpenAPI <h1>, not the HTML <title>, which is defined in add_api_routes def openapi_docs()
                title=uvicore.config('app.api.openapi.title'),

                # Get version from main running apps package.version
                version=uvicore.app.package(main=True).version,

                # NOTE: Most other info is provided in my add_api_routes def openapi_docs() override

                #openapi_url=uvicore.config('app.api.openapi.url'),
                #swagger_ui_oauth2_redirect_url=uvicore.config('app.api.openapi.docs_url') + '/oauth2-redirect',

                # Default FastAPI docs and redoc routes
                #docs_url=uvicore.config('app.api.openapi.docs_url'),
                #redoc_url=uvicore.config('app.api.openapi.redoc_url'),

                # DISABLE the /docs and /redoc URLs
                # Why?  Because we add our own CUSTOM one later in add_api_routes()
                docs_url=None,

                # DISABLE redoc
                # Can leave redoc on for now, maybe add to config to change /redoc path
                redoc_url=None,

                #swagger_ui_oauth2_redirect_url=

                #root_path='/api',  #fixme with trying out kong
            )



        ############ ORIGINAL BELOW

        # # Base server is Starlette
        # if web_routes and api_routes:
        #     base_server = Starlette(
        #         debug=debug,
        #     )

        # # Web server is FastAPI with NO OpenAPI setup
        # if web_routes:
        #     if USE_STARLETTE:
        #         # Try a pure starlette server
        #         web_server = Starlette(debug=debug)
        #     else:
        #         web_server = FastAPI(
        #             debug=debug,
        #             version=uvicore.app.version,
        #             openapi_url=None,
        #             swagger_ui_oauth2_redirect_url=None,
        #         )

        # # Api server is FastAPI with OpenAPI setup
        # if api_routes:
        #     api_server = FastAPI(
        #         debug=debug,

        #         # This title is what shows up in OpenAPI <h1>, not the HTML <title>, which is defined in add_api_routes def openapi_docs()
        #         title=uvicore.config('app.api.openapi.title'),

        #         # Get version from main running apps package.version
        #         version=uvicore.app.package(main=True).version,

        #         # NOTE: Most other info is provided in my add_api_routes def openapi_docs() override

        #         #openapi_url=uvicore.config('app.api.openapi.url'),
        #         #swagger_ui_oauth2_redirect_url=uvicore.config('app.api.openapi.docs_url') + '/oauth2-redirect',

        #         # Default FastAPI docs and redoc routes
        #         #docs_url=uvicore.config('app.api.openapi.docs_url'),
        #         #redoc_url=uvicore.config('app.api.openapi.redoc_url'),

        #         docs_url=None,
        #         redoc_url=None,

        #         #swagger_ui_oauth2_redirect_url=

        #         #root_path='/api',  #fixme with trying out kong
        #     )
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

    def add_exception_handlers(self, web_server: FastAPI, api_server: FastAPI) -> None:
        """Add global web and api exception handlers to their respective servers"""
        from starlette.exceptions import HTTPException

        # Add global web exception handlers
        if web_server and uvicore.config.app.web.exception.handler:
            cls = module.load(uvicore.config.app.web.exception.handler).object
            web_server.add_exception_handler(HTTPException, cls)
            # for name, handler in uvicore.config.app.web.exceptions.items():
            #     if str(name).lower() == 'main':
            #         cls = module.load(handler).object
            #         web_server.add_exception_handler(HTTPException, cls)

        # Add global api exception handlers
        if api_server and uvicore.config.app.api.exception.handler:
            cls = module.load(uvicore.config.app.api.exception.handler).object
            api_server.add_exception_handler(HTTPException, cls)

            # for name, handler in uvicore.config.app.api.exceptions.items():
            #     if str(name).lower() == 'main':
            #         cls = module.load(handler).object
            #         api_server.add_exception_handler(HTTPException, cls)

        #dump(api_server.__dict__)
        #dump(web_server.__dict__)

    def add_web_routes(self, web_server, web_routes: Dict[str, WebRoute]) -> None:
        """Add web routes to the web server"""

        # Do nothing if no api_routes are defined
        if not web_routes: return

        for route in web_routes.values():
            if USE_STARLETTE:
                # Starlette
                web_server.add_route(
                    path=route.path,
                    route=route.endpoint,
                    methods=route.methods,
                    name=route.name,
                    include_in_schema=False,
                )
            else:
                # FastAPI
                web_server.add_api_route(
                    path=route.path or '/',
                    endpoint=route.endpoint,
                    methods=route.methods,
                    name=route.name,
                    include_in_schema=False,
                    response_class=response.HTML,
                    dependencies=route.middleware,
                )

    def add_api_routes(self, api_server, api_routes: Dict[str, ApiRoute]) -> None:
        """Add api routes to the api server"""

        # Do nothing if no api_routes are defined
        if not api_routes: return

        # Get important app configs
        api_prefix = self.get_prefix('app.api.prefix')
        openapi = uvicore.config.app.api.openapi
        rapidoc = uvicore.config.app.api.rapidoc
        oauth2 = uvicore.config.app.auth.oauth2

        # Determine if OpenAPI docs oauth2 authentication is enabled
        # If OpenAPI oauth2 is enabled, create a FastAPI OAuth2AuthorizationCodeBearer variable
        if openapi.oauth2_enabled and oauth2:
            from fastapi.security import OAuth2AuthorizationCodeBearer
            oauth2_scheme = OAuth2AuthorizationCodeBearer(
                authorizationUrl=oauth2.base_url + oauth2.authorize_path,
                tokenUrl=oauth2.base_url + oauth2.token_path,
            )

        # Create our own custom RapiDoc docs route
        if rapidoc.path and openapi.path:

            # Oauth2 redirect URL (without api_prefid)
            rapidoc_redirect_url =  rapidoc.path + '/oauth-receiver.html'

            @api_server.get(rapidoc.path, include_in_schema=False)
            def rapidoc_docs():
                return get_rapidoc_ui_html(
                    openapi_url=api_prefix + openapi.path,
                )

            @api_server.get(rapidoc.pdf_path, include_in_schema=False)
            def rapidoc_docs():
                return get_rapidoc_pdf_ui_html(
                    openapi_url=api_prefix + openapi.path,
                )

            @api_server.get(rapidoc_redirect_url, include_in_schema=False)
            def rapidoc_redirect():
                return get_rapidoc_ui_oauth2_redirect_html()


        # Create our own custom OpenAPI docs route
        if openapi.path and openapi.docs.path:

            # Oauth2 redirect URL (without api_prefid)
            openapi_redirect_url =  openapi.docs.path + '/login'

            @api_server.get(openapi.docs.path, include_in_schema=False)
            def openapi_docs():
                return get_swagger_ui_html(

                    # Define our openapi.json path from prefix and config
                    openapi_url=api_prefix + openapi.path,
                    oauth2_redirect_url=api_prefix + openapi_redirect_url,

                    # This title is html <title> while the title in app_server = FastAPI is what shows up in OpenAPI <h1> title, I make them the same
                    title=openapi.title,

                    # Swagger urls
                    swagger_favicon_url=openapi.docs.favicon_url,
                    swagger_js_url=openapi.docs.js_url,
                    swagger_css_url=openapi.docs.css_url,

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
                    doc_expansion=openapi.docs.expansion.lower() or 'list'
                )

            @api_server.get(openapi_redirect_url, include_in_schema=False)
            def openapi_redirect():
                return get_swagger_ui_oauth2_redirect_html()


        # Loop each uvicore route and add as FastAPI route
        for route in api_routes.values():
            # ----------------------------------------------------------------------------------
            # NO, all of this moved into api_router.py so I can see it at the package definition (./uvicore package list) level
            # ----------------------------------------------------------------------------------
            # endpoint_func = route.endpoint
            # response_model = route.response_model

            # # If endpoint is partial, grab inside func for type hindint and docstrings
            # if isinstance(route.endpoint, partial):
            #     # Endpoint is a partial (was overwritten to default some higher order middleware)
            #     # A partial overwrites the original docstring.  Functools update_wrapper will copy it back
            #     # as well as handle merging of other important properties
            #     #update_wrapper(route.endpoint, route.endpoint.func)
            #     endpoint_func = route.endpoint.func

            #     # Blank out the __doc__ on actual Partial itself, not actual endpoint inside partial.
            #     # If not, OpenAPI doc description will be partial(func, *args, **keywords) - new function with partial application etc...
            #     route.endpoint.__doc__ = None

            # # Get response model from parameter or infer from endpoint return type hint
            # #response_model = route.response_model if route.response_model else get_type_hints(endpoint_func).get('return')
            # response_model = route.response_model or get_type_hints(endpoint_func).get('return')

            # # Get openapi description from route param or endpoint docstring
            # description = route.description or endpoint_func.__doc__
            # ----------------------------------------------------------------------------------

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
                #path=(prefix + route.path) or '/',
                path=(route.path) or '/',
                endpoint=route.endpoint,
                methods=route.methods,
                name=route.name,
                response_model=route.response_model,
                response_class=route.response_class or response.JSONResponse,
                responses=route.responses,
                tags=route.tags,
                dependencies=route.middleware,
                summary=route.summary,
                description=route.description,
            )

    def configure_webserver(self, web_server) -> None:
        """Configure the webserver with public, assets, views, composers and template options"""

        # Ignore if web_server was never fired up
        if not web_server: return

        # Loop each package with an HTTP definition and add to our HTTP server
        public_paths = []
        asset_paths = []
        view_paths = []
        view_composers = Dict()
        context_processors = Dict()
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

            # Deep merge view composers
            view_composers.merge(package.web.view_composers or {})

            # Deep merge template options
            context_processors.merge(package.web.context_processors or {})

        # Save merged view composers into our config for use later (in http/response View() )
        uvicore.config.uvicore.http.view_composers = view_composers

        #dd(view_composers)

        # Mount all static paths
        self.mount_static(web_server, public_paths, asset_paths)

        # Initialize new template environment from the options above
        self.initialize_templates(view_paths, context_processors)

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

    def initialize_templates(self, paths, context_processors) -> None:
        """Initialize and configure template system"""
        # Get the template singleton from the IoC
        templates = uvicore.ioc.make('uvicore.templating.engine.Templates')

        # Add all packages view paths
        # First path wins, so we must REVERSE the package order
        # This will set the main running app FIRST as we always want the app to win
        paths.reverse()
        for path in paths:
            templates.include_path(module.location(path))

        # Add all packages deep_merged template context_processors
        if 'context_functions' in context_processors:
            for name, method in context_processors['context_functions'].items():
                templates.include_context_function(name, method)
        if 'context_filters' in context_processors:
            for name, method in context_processors['context_filters'].items():
                templates.include_context_filter(name, method)
        if 'filters' in context_processors:
            for name, method in context_processors['filters'].items():
                templates.include_filter(name, method)
        if 'tests' in context_processors:
            for name, method in context_processors['tests'].items():
                templates.include_test(name, method)

        # Initialize template system
        templates._init()

    def get_prefix(self, confpath: str) -> str:
        """Get configured web and api prefixes ensuring "" prefix and no trailing /, or / if blank)"""
        prefix = uvicore.config(confpath)
        #if not prefix: prefix = '/'
        #if prefix != '/' and prefix[-1] == '/': prefix = prefix[0:-1]  # No trailing /
        if prefix and prefix[-1] == '/': prefix = prefix[0:-1]  # No trailing /
        return prefix
