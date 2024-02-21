import uvicore
from uvicore.package import Provider
from uvicore.http.package import bootstrap
from uvicore.support.dumper import dump, dd
from uvicore.http.package.registers import Http
from uvicore.console.package.registers import Cli
from uvicore.foundation.events import app as AppEvents


@uvicore.provider()
class Http(Provider, Cli, Http):

    def register(self) -> None:
        """Register package into the uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs, IoC bindings and early event listeners.
        Configs are deep merged only after all packages are registered.  No real
        work should be performed here as it is very early in the bootstraping
        process and we have no clear view of the full configuration system."""

        # Register events used in this package
        # NO, moved to events/server.py using @uvicore.event() to auto-register event list.
        # self.events.register(
        #     name='uvicore.http.events.server.Startup',
        #     description='HTTP Server has been started.  This is the Starlette startup event.',
        #     is_async=False,
        # )
        # self.events.register(
        #     name='uvicore.http.events.server.Shutdown',
        #     description='HTTP Server has been shutdown.  This is the Starlette shutdown event.',
        #     is_async=False,
        # )

        #     @uvicore.app.http.on_event("shutdown")
        #     async def shutdown():
        #         for database in self.databases.values():
        #             await database.disconnect()

        # Register event listeners
        # After all providers are booted we have a complete list of view paths
        # and template options fully merged.  Now we can fire up the static
        # paths and template system.
        # We handle this event even in CONSOLE mode to handle edge cases.
        AppEvents.Booted.listen(bootstrap.Http)


        # Register IoC bindings only if running in HTTP mode
        #if self.app.is_http:

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
            #self.bind('Templates', 'uvicore.http.templating.jinja.Jinja', singleton=True, aliases=['templates'])

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

    def boot(self) -> None:
        """Bootstrap package into the uvicore framework.
        Boot takes place after ALL packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all
        configuration. This is where you register, connections, models,
        views, assets, routes, commands...  If you need to perform work after ALL
        packages have booted, use the event system and listen to the booted event:
        self.events.listen('uvicore.foundation.events.app.Booted', self.booted)"""

        # Define service provider registration control
        self.registers(self.package.config.registers)

        # Define HTTP Middleware
        #self.middleware(uvicore.config('app.middleware'))

        # Define CLI commands
        self.register_cli_commands({
            'http': {
                'help': 'Uvicore HTTP Commands',
                'commands': {
                    'serve': 'uvicore.http.commands.serve.cli',
                    'routes': 'uvicore.http.commands.routes.list',
                },
            },

            # Extend schematic generator commands
            'gen': {
                'commands': {
                    'controller': 'uvicore.http.commands.generators.controller',
                    'api-controller': 'uvicore.http.commands.generators.api_controller',
                    'composer': 'uvicore.http.commands.generators.composer',
                },
            }
        })

        # Uvicore default template options.  Because this HTTP package is high up
        # your package can easily override any of these default options!
        from uvicore.http.templating import context_functions
        self.register_http_view_context_processors({
            'context_functions': {
                'url': context_functions.url,
                'asset': context_functions.asset,
                'public': context_functions.public,
            },
        })

