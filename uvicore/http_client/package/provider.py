import uvicore
import aiohttp
from uvicore.package import Provider
from uvicore.support.dumper import dump, dd


@uvicore.provider()
class HttpClient(Provider):

    def register(self) -> None:
        """Register package into the uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs, IoC bindings and early event listeners.
        Configs are deep merged only after all packages are registered.  No real
        work should be performed here as it is very early in the bootstraping
        process and we have no clear view of the full configuration system."""

        # Register event listeners
        # String based events instead of class based because HTTP may not even
        # be installed, so importing it would cause an issue.
        @uvicore.events.handle(['uvicore.console.events.command.Startup', 'uvicore.console.events.command.PytestStartup', 'uvicore.http.events.server.Startup'])
        async def uvicore_startup(event):
            #print('aiohttp console/http startup')
            # Fire up an aiohttp client session and bind to IoC as a singleton
            uvicore.ioc.bind('uvicore.http_client', aiohttp.ClientSession(),
                aliases=['http_client', 'aiohttp'],
                singleton=True
            )

        @uvicore.events.handle(['uvicore.console.events.command.Shutdown', 'uvicore.console.events.command.PytestShutdown', 'uvicore.http.events.server.Shutdown'])
        async def uvicore_shutdown(event):
            #print('aiohttp console/http shutdown')
            # Shutdown the aiohttp client session
            await uvicore.ioc.make('aiohttp').close()

    def boot(self) -> None:
        """Bootstrap package into the uvicore framework.
        Boot takes place after ALL packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all
        configuration. This is where you register, connections, models,
        views, assets, routes, commands...  If you need to perform work after ALL
        packages have booted, use the event system and listen to the booted event:
        self.events.listen('uvicore.foundation.events.app.Booted', self.booted)"""

        pass
