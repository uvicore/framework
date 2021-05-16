import uvicore
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd
from uvicore.foundation.events import app as AppEvents


@uvicore.provider()
class Cache(ServiceProvider):

    def register(self) -> None:
        # Register event listeners
        #AppEvents.Registered.listen(bootstrap.Cache)

        #self.bind_override('uvicore.cache.cache.Cache', 'uvicore.cache.cache2.Cache2')
        # self.bind('uvicore.cache.cache.Cache', 'uvicore.cache.cache.Cache',
        #     aliases=['cache0', 'cache'],
        #     singleton=False,
        # )

        #self.bind('uvicore.cache.cache.Cache')

        # self.bind('uvicore.cache.cache.Cache', 'uvicore.cache.cache2.Cache2',
        #     aliases=['cacheO'],
        #     singleton=True,
        # )

        # Set uvicore.log global connecting to default store
        uvicore.cache = uvicore.ioc.make('uvicore.cache.manager.Manager').connect()

    def boot(self) -> None:
        # Define service provider registration control
        #self.registers(self.package.config.registers)

        # Import cache to fire up Ioc so we can later use as short 'cache' names
        #from uvicore.cache.cache import Cache
        pass
