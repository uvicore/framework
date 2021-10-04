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

        # Event Handlers
        # String based events instead of class based because HTTP may not even
        # be installed, so importing the HTTP event would cause an issue.

        # Disconnect from all redis pools after the system has shutdown
        @uvicore.events.handle(['uvicore.console.events.command.Shutdown', 'uvicore.http.events.server.Shutdown'])
        async def uvicore_shutdown(event):
            # Trying to solve this error when I do a huge wrk test
            # Task was destroyed but it is pending!
            # task: <Task pending name='Task-13' coro=<RedisConnection._read_data() running at /home/mreschke/.cache/pypoetry/virtualenvs/mreschke-speedtest-epfwGmSK-py3.9/lib/python3.9/site-packages/aioredis/connection.py:186> wait_for=<Future pending cb=[<TaskWakeupMethWrapper object at 0x7f6043f7ac10>()]> cb=[RedisConnection.__init__.<locals>.<lambda>() at /home/mreschke/.cache/pypoetry/virtualenvs/mreschke-speedtest-epfwGmSK-py3.9/lib/python3.9/site-packages/aioredis/connection.py:168]>
            # See https://github.com/aio-libs/aioredis-py/issues/154
            # I am doing the proper engine.close() and await engine.wait_closed() and it does run before I get the error
            # but the error persists.  Still not fully solved, but closing does help in some situations
            redis = uvicore.ioc.make('uvicore.redis.redis.Redis')
            for engine in redis.engines.values():
                engine.close()
                await engine.wait_closed()

    def boot(self) -> None:
        pass
        # Define service provider registration control
        #self.registers(self.package.config.registers)

        # Define Redis Connections
        # self.redis_connections(
        #     connections=self.package.config.redis.connections,
        #     default=self.package.config.redis.default
        # )
