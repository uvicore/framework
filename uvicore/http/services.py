import uvicore
from uvicore.typing import Dict, Any
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd
from uvicore.support.module import load, location
from uvicore.support.dictionary import deep_merge
from uvicore.console.provider import Cli
from uvicore.http.provider import Http



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

            # Set app instance variables
            self.app._http = uvicore.ioc.make('uvicore.http.server._Server')

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
                'url': context_functions.url
            },
        })

    def booted(self, event: str, payload: Any) -> None:
        """Custom event handler for uvicore.foundation.events.app.Booted"""
        # This function only runs if in HTTP mode, not CLI mode.
        # So no need to check if running as HTTP in each function below!
        # But we'll double check here just in case.
        if self.app.is_console: return

        # Loop each package with an HTTP definition and add to our HTTP server
        asset_paths = []
        view_paths = []
        template_options = {}
        for package in self.app.packages.values():
            if not 'http' in package: continue

            # Add web and API routes for this one package
            self.add_web_routes(package)
            self.add_api_routes(package)

            # Append asset paths for later
            for path in package.http.asset_paths or []:
                path_location = location(path)
                if path_location not in asset_paths: asset_paths.append(path_location)

            # Append template paths
            for path in package.http.view_paths or []:
                view_paths.append(path)

            # Deep merge template options
            template_options = deep_merge(package.http.template_options or {}, template_options)

        # Mount all static asset paths
        self.mount_static_assets(package, asset_paths)

        # Initialize new template environment from the options above
        self.initialize_templates(view_paths, template_options)

    def add_web_routes(self, package) -> None:
        """Import and load this one packages web routes"""
        # Dont load items if registration is disabled
        if not package.registers.web_routes: return

        # Do not load if no web_routes defined
        if not 'web_routes' in package.http: return

        # Import and instantiate apps WebRoutes class
        from uvicore.http.routing.web_router import WebRouter
        WebRoutes = load(package.http.web_routes).object
        routes = WebRoutes(uvicore.app, package, WebRouter, package.http.web_route_prefix)
        routes.register()

    def add_api_routes(self, package) -> None:
        """Import and load this one packages api routes"""
        # Dont load items if registration is disabled
        if not package.registers.api_routes: return

        # Do not load if no web_routes defined
        if not 'api_routes' in package.http: return

        # Import and instantiate apps ApiRoutes class
        from uvicore.http.routing.api_router import ApiRouter
        ApiRoutes = load(package.http.api_routes).object
        routes = ApiRoutes(uvicore.app, package, ApiRouter, package.http.api_route_prefix)
        routes.register()

    def mount_static_assets(self, package, asset_paths) -> None:
        """Mount /static route using all packages static paths"""
        StaticFiles = uvicore.ioc.make('uvicore.http.static._StaticFiles')

        # Mount all directories to /assets in one go
        # Last directory defined WINS, which fits our last provider wins
        self.app.http.mount('/static', StaticFiles(directories=asset_paths), name='static')

    def initialize_templates(self, paths, options) -> None:
        """Initialize template system"""
        # Get the template singleton from the IoC
        templates = uvicore.ioc.make('uvicore.http.templating.jinja._Jinja')

        # Add all packages view paths
        for path in paths:
            templates.include_path(location(path))

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

