import uvicore
from typing import Dict, Any
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd

@uvicore.provider()
class Http(ServiceProvider):

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
        # Register HTTP Serve commands
        self.commands([
            {
                'group': {
                    'name': 'http',
                    'parent': 'root',
                    'help': 'Uvicore HTTP Commands',
                },
                'commands': [
                    {'name': 'serve', 'module': 'uvicore.http.commands.serve.cli'},
                ],
            }
        ])

    def booted(self, event: str, payload: Any) -> None:
        """Custom event handler for uvicore.foundation.events.booted"""
        self.mount_static_assets()
        self.create_template_environment()

    def mount_static_assets(self) -> None:
        """Mount /static route using all packages static paths"""
        StaticFiles = uvicore.ioc.make('uvicore.http.static._StaticFiles')

        # Get all packages asset paths
        paths = []
        for package in self.app.packages.values():
            for path in package.asset_paths:
                if path not in paths:
                    paths.append(path)

        # Mount all directories to /assets
        # Last directory defined WINS, which fits our last provider wins
        self.app.http.mount('/static', StaticFiles(directories=paths), name='static')

    def create_template_environment(self) -> None:
        """Create template environment with settings from all packages"""

        # Get the template singleton from the IoC
        templates = uvicore.ioc.make('uvicore.http.templating.jinja._Jinja')

        # Add all package view paths to template environment
        for package in self.app.packages.values():
            for path in package.view_paths:
                templates.include_path(path)

            # Add all package template options to template environment
            options = package.template_options
            if 'context_functions' in options:
                for f in options['context_functions']:
                    templates.include_context_function(**f)
            if 'context_filters' in options:
                for f in options['context_filters']:
                    templates.include_context_filter(**f)
            if 'filters' in options:
                for f in options['filters']:
                    templates.include_filter(**f)
            if 'tests' in options:
                for f in options['tests']:
                    templates.include_test(**f)

        # Initialize new template environment from the options above
        templates.init()
