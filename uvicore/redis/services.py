import uvicore
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd
from uvicore.redis import bootstrap
from uvicore.foundation.events import app as AppEvents
from uvicore.redis.provider import Redis as RedisMixin


@uvicore.provider()
class Redis(ServiceProvider, RedisMixin):

    def register(self) -> None:
        # Register event listeners
        AppEvents.Booted.listen(bootstrap.Redis)


    def boot(self) -> None:
        pass
        # Define service provider registration control
        #self.registers(self.package.config.registers)

        # Define Redis Connections
        # self.redis_connections(
        #     connections=self.package.config.redis.connections,
        #     default=self.package.config.redis.default
        # )
