import uvicore
import httpx
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
            #print('httpx console/http startup')
            # Fire up an httpx async client and bind to IoC as a singleton
            uvicore.ioc.bind('uvicore.http_client', httpx.AsyncClient(),
                aliases=['http_client', 'httpx'],
                singleton=True
            )

        @uvicore.events.handle(['uvicore.console.events.command.Shutdown', 'uvicore.console.events.command.PytestShutdown', 'uvicore.http.events.server.Shutdown'])
        async def uvicore_shutdown(event):
            #print('httpx console/http shutdown')
            # Shutdown the httpx async client, but only if it was ever bound.
            # The matching startup event does not always fire in the same process
            # that fires shutdown.  For example `uvicore http serve` runs the actual
            # http server (which fires the server Startup) in a uvicorn reload worker
            # subprocess, while the console Shutdown fires later in the parent process
            # where http_client was never bound.  Guard against that so ctrl+c does
            # not raise ModuleNotFoundError.
            if uvicore.ioc.binding('http_client'):
                await uvicore.ioc.make('http_client').aclose()

    def boot(self) -> None:
        """Bootstrap package into the uvicore framework.
        Boot takes place after ALL packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all
        configuration. This is where you register, connections, models,
        views, assets, routes, commands...  If you need to perform work after ALL
        packages have booted, use the event system and listen to the booted event:
        self.events.listen('uvicore.foundation.events.app.Booted', self.booted)"""

        pass
