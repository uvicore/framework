import uvicore
import aiohttp
from uvicore.package import Provider
from uvicore.support.dumper import dump, dd


@uvicore.provider()
class HttpClient(Provider):

    def register(self) -> None:

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
        pass
