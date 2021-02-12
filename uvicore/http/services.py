import uvicore
from uvicore.typing import Dict, Any, List, OrderedDict
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd
from uvicore.support import module
from uvicore.support.dictionary import deep_merge
from uvicore.console.provider import Cli
from uvicore.http.provider import Http
from starlette.applications import Starlette as _Starlette
from fastapi import FastAPI as _FastAPI


@uvicore.provider()
class Http(ServiceProvider, Cli, Http):

    def register(self) -> None:
        """Register package into uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs and IoC bindings.  Configs are deep merged only after
        all packages are registered.  No real work should be performed here as it
        is very early in the bootstraping process and most internal processes are not
        instantiated yet.
        """

        # Register IoC bindings only if running in HTTP mode
        if self.app.is_http:

            # # Bind HTTP Server
            # self.bind('Http', 'uvicore.http.server._Server',
            #     aliases=['uvicore.http.server.Server', 'http', 'HTTP'],
            #     singleton=True,
            #     kwargs={
            #         'debug': uvicore.config('app.debug'),
            #         'title': uvicore.config('app.openapi.title'),
            #         'version': uvicore.app.version,
            #         'openapi_url': uvicore.config('app.openapi.url'),
            #         'docs_url': uvicore.config('app.openapi.docs_url'),
            #         'redoc_url': uvicore.config('app.openapi.redoc_url'),
            #     }
            # )
            # No because I added default to make
            #self.bind('WebRouter', 'uvicore.http.routing.web_router._WebRouter', aliases=['uvicore.http.routing.web_router.WebRouter', 'web_router'])
            #self.bind('ApiRouter', 'uvicore.http.routing.api_router._ApiRouter', aliases=['uvicore.http.routing.api_router.ApiRouter', 'api_router'])
            #self.bind('Routes', 'uvicore.http.routing.routes._Routes', aliases=['uvicore.http.routing.routes.Routes', 'routes'])
            #self.bind('StaticFiles', 'uvicore.http.static._StaticFiles', aliases=['Static', 'static'])

            # Default templating system is Jinja2.  Users can overwrite this
            # easily in their app configs 'bindings' dictionary.
            #self.bind('Templates', 'uvicore.http.templating.jinja._Jinja', singleton=True, aliases=['templates'])

            # Fire up a FastAPI server instance and store on app.http
            #self.app._http = uvicore.ioc.make('uvicore.http.server._Server')
            #self.app._http = uvicore.ioc.make('uvicore.http.servers.api._Server')  # FastAPI as Base
            #self.app._http = uvicore.ioc.make('uvicore.http.servers.web._Server')  # Starlette as Base

            # Base HTTP Server
            #self.app._http = uvicore.ioc.make('uvicore.http.servers.api._Server')  # FastAPI as Base
            # self.app._http: _FastAPI = _FastAPI(
            #     debug=uvicore.config('app.debug'),
            #     title=uvicore.config('app.openapi.title'),
            #     version=uvicore.app.version,
            #     openapi_url=uvicore.config('app.openapi.url'),
            #     docs_url=uvicore.config('app.openapi.docs_url'),
            #     redoc_url=uvicore.config('app.openapi.redoc_url'),
            #     root_path='/api',
            # )


            # Register event listeners
            # After all providers are booted we have a complete list of view paths
            # and template options fully merged.  Now we can fire up the static
            # paths and template system.
            self.events.listen('uvicore.foundation.events.app.Booted', self.booted)

    def boot(self) -> None:
        """Bootstrap package into uvicore framework.
        Boot takes place after all packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all configs.
        This is where you load views, assets, routes, commands...
        """
        # Define service provider registration control
        self.registers(self.package.config.registers)

        # Define HTTP Middleware
        #self.middleware(uvicore.config('app.middleware'))

        # Define CLI commands
        self.commands({
            'http': {
                'help': 'Uvicore HTTP Commands',
                'commands': {
                    'serve': 'uvicore.http.commands.serve.cli',
                },
            }
        })

        # Uvicore default template options.  Because this HTTP package is high up
        # your package can easily override any of these default options!
        from uvicore.http.templating import context_functions
        self.template({
            'context_functions': {
                'url': context_functions.url,
                'asset': context_functions.asset,
                'public': context_functions.public,
            },
        })

    def booted(self, event: str, payload: Any) -> None:
        """Custom event handler for uvicore.foundation.events.app.Booted"""
        # This event handlers if only fired if running in  HTTP mode.
        # So technically we don't need to explicitly check if HTTP here, but
        # we'll double check just in case.
        if not self.app.is_http: return

        # Merge all packages Web and Api routes
        web_routes = Dict()
        api_routes = Dict()
        for package in self.app.packages.values():
            # Merging in package order ensures last package wins!
            if package.web.routes:
                web_routes.merge(package.web.routes)
            if package.api.routes:
                api_routes.merge(package.api.routes)

        # If no routes, do nothing, no HTTP server at all
        if not web_routes and not api_routes: return

        # Fire up our base HTTP server.  If we have both web and api routes
        # then we will submount subservers, if not, we will only  use one server
        base_server = None
        web_server = None
        api_server = None
        debug = uvicore.config('app.debug'),
        if web_routes and api_routes:
            # Base server is FastAPI with NO OpenAPI setup
            base_server = _FastAPI(
                debug=debug,
                version=uvicore.app.version,
                openapi_url=None,
                swagger_ui_oauth2_redirect_url=None,
            )

        if web_routes:
            web_server = _FastAPI(
                debug=debug,
                version=uvicore.app.version,
                openapi_url=None,
                swagger_ui_oauth2_redirect_url=None,
            )

        if api_routes:
            api_server = _FastAPI(
                debug=debug,
                title=uvicore.config('app.api.openapi.title'),
                version=uvicore.app.version,
                openapi_url=uvicore.config('app.api.openapi.url'),
                swagger_ui_oauth2_redirect_url=uvicore.config('app.api.openapi.docs_url') + '/oauth2-redirect',
                docs_url=uvicore.config('app.api.openapi.docs_url'),
                redoc_url=uvicore.config('app.api.openapi.redoc_url'),
                #root_path='/api',  #fixme with trying out kong
            )

        # Add web middleware
        if web_server:
            for name, middleware in uvicore.config.app.web.middleware.items():
                cls = module.load(middleware.module).object
                web_server.add_middleware(cls, **middleware.options)

        # Add api middleware
        if api_server:
            for name, middleware in uvicore.config.app.api.middleware.items():
                cls = module.load(middleware.module).object
                api_server.add_middleware(cls, **middleware.options)

        # Add Web Routes to their servers
        for route in web_routes.values():
            web_server.add_route(
                path=route.path,
                route=route.endpoint,
                methods=route.methods,
                name=route.name,
            )

        # Add Web Routes to their servers
        for route in api_routes.values():
            api_server.add_api_route(
                path=route.path,
                endpoint=route.endpoint,
                methods=route.methods,
                name=route.name,
            )

        if base_server:
            # Longer prefix has to be FIRST to match subapp regex properly
            web_prefix = uvicore.config('app.web.prefix')
            api_prefix = uvicore.config('app.api.prefix')
            if len(web_prefix) > len(api_prefix):
                base_server.mount(web_prefix, web_server)  # Web first
                base_server.mount(api_prefix, api_server)
            else:
                base_server.mount(api_prefix, api_server)  # Api first
                base_server.mount(web_prefix, web_server)
            self.app._http = base_server
        elif web_server:
            self.app._http = web_server
        elif api_server:
            self.app._http = api_server

        # Debug and dump the actual HTTP servers (base, web, api) info and routes
        debug_dump = True
        if debug_dump:
            dump('#################################################################')
            dump("Main HTTP Server APPLICATION", self.app.http.__dict__)

            dump('#################################################################')
            dump("Main HTTP Server Routes")
            for route in self.app.http.routes:
                dump(route.__dict__)

            for route in self.app.http.routes:
                if route.name is None:
                    dump('#################################################################')
                    dump("Sub Server '{}' APPLICATION".format(route.path))
                    dump(route.app.__dict__)

                    dump('#################################################################')
                    dump("Sub Server '{}' Routes".format(route.path))
                    for r in route.app.router.routes:
                        dump(r.__dict__)



        # DONE -------------------------------------
        return



        # Mount web into api
        #api.mount('/', web)

        # Order matters, lowest root / comes LAST
        #self.app.http.mount('/api', api)
        self.app.http.mount('/', api)


            #if route.path == '':
            #     for web_route in route.app.router.routes:
            #         dump(web_route.__dict__)
            # elif route.path == '/api':
            #     for api_route in route.app.router.routes:
            #         dump(api_route.__dict__)
            # else:
            #     dump(route.__dict__)

        #dd('x')

        # EXIT
        return



        # Add app global middleware (middleware is NOT per pacakge)
        # Note starlette handles the order exactly as we defined in our OrderedDict
        # but it adds starlette.exceptions.ExceptionMiddleware BEFORE
        # and starlette.middleware.errors.ServerErrorMiddleware AFTER all user defined middleware
        for name, middleware in uvicore.config.app.middleware.items():
            cls = module.load(middleware.module).object
            self.app.http.server.add_middleware(cls, **middleware.options)


        # Experiment add custom exceptions
        from uvicore.http import response
        async def internal_server_error_500(request, exc):
            print(exc)
            return response.HTML(content='custom 500 internal server error', status_code=500)

        async def not_found_404(request, exc):
            print(exc)
            return response.HTML(content='custom 404 not found', status_code=505)

        self.app.http.server.add_exception_handler(500, internal_server_error_500)
        self.app.http.server.add_exception_handler(404, not_found_404)
        dump('xxxxxx', self.app.http.server.exception_handlers)


        # Loop each package with an HTTP definition and add to our HTTP server
        public_paths = []
        asset_paths = []
        view_paths = []
        template_options = {}
        for package in self.app.packages.values():
            #if not 'http' in package: continue
            if not 'web' in package: continue

            # Add web and API routes for this one package
            self.add_web_routes(package)
            #self.add_api_routes(package)

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
            template_options = deep_merge(package.web.template_options or {}, template_options)

        # Mount all static paths
        self.mount_static(package, public_paths, asset_paths)

        # Initialize new template environment from the options above
        self.initialize_templates(view_paths, template_options)

    def add_web_routes(self, package) -> None:
        """Import and load this one packages web routes"""
        # Dont load items if registration is disabled
        if not package.registers.web_routes: return

        # Do not load if no web_routes defined
        #if not 'web_routes' in package.http: return
        if not 'routes_module' in package.web: return

        # # Import and instantiate apps WebRoutes class
        # from uvicore.http.routing.web_router import WebRouter
        # WebRoutes = module.load(package.http.web_routes).object
        # routes = WebRoutes(uvicore.app, package, WebRouter, package.http.web_route_prefix)
        # routes.register()

        routes_module = package.web.routes_module
        dd(routes_module)



    def add_api_routes(self, package) -> None:
        """Import and load this one packages api routes"""
        # Dont load items if registration is disabled
        if not package.registers.api_routes: return

        # Do not load if no web_routes defined
        if not 'api_routes' in package.http: return

        # Import and instantiate apps ApiRoutes class
        from uvicore.http.routing.api_router import ApiRouter
        ApiRoutes = module.load(package.http.api_routes).object
        routes = ApiRoutes(uvicore.app, package, ApiRouter, package.http.api_route_prefix)
        router = routes.routes()
        uvicore.app.http.include_router(router)

    def mount_static(self, package, public_paths: List, asset_paths: List) -> None:
        """Mount /static route using all packages static paths"""
        StaticFiles = uvicore.ioc.make('uvicore.http.static._StaticFiles')

        # Last directory defined WINS, which fits our last provider wins

        # Mount all asset paths
        asset_url = uvicore.config.app.asset.path or '/assets'
        self.app.http.mount(asset_url, StaticFiles(directories=asset_paths), name='assets')

        # Mount all public paths (always at /)
        # Since it is root / MUST be defined last or it wins above any path after it
        self.app.http.mount('/', StaticFiles(directories=public_paths), name='public')

    def initialize_templates(self, paths, options) -> None:
        """Initialize template system"""
        # Get the template singleton from the IoC
        templates = uvicore.ioc.make('uvicore.http.templating.jinja._Jinja')

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

