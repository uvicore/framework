import uvicore
import aioredis
from uvicore.typing import Dict, Any
from uvicore.support.dumper import dump, dd

# Basically a uvicore quick connect and passthrough of aioredis
# For aioredis commands see https://aioredis.readthedocs.io/en/latest/mixins.html#generic-commands

@uvicore.service('uvicore.redis.redis.Redis',
    aliases=['Redis', 'redis'],
    singleton=True,
)
class Redis:

    @property
    def default(self) -> str:
        return self._default

    @property
    def connections(self) -> Dict[str, str]:
        return self._connections

    @property
    def engines(self) -> Dict:
        """All connected redis pools"""
        return self._engines

    def __init__(self) -> None:
        self._default = None
        self._connections = Dict()
        self._engines = Dict()

    def init(self, default: str, connections: Dict[str, str]):
        self._default = default
        self._connections = connections
        for connection in self.connections.values():
            connection.url = (
                'redis://'
                + connection.host + ':'
                + str(connection.port) + '/'
                + str(connection.database)
            )
            if connection.password:
                connection.url += '?password=' + connection.password

    def connection(self, connection: str = None):
        """Get one connection by name"""
        if not connection: connection = self.default
        conn = self.connections.get(connection)
        if not conn:
            raise Exception('Redis connection {} not found'.format(connection))
        return conn

    async def connect(self, connection: str = None) -> aioredis.Redis:
        """Connect to a redis database by uvicore connection"""
        conn = self.connection(connection)

        # Connect to redis pool if connection never started
        if conn.url not in self.engines:
            # Dict({
            # 'host': '127.0.0.1',
            # 'port': 6379,
            # 'database': 2,
            # 'password': None,
            # 'url': 'redis://127.0.0.1:6379/2'
            # })
            #self._engines[conn.url] = await aioredis.create_redis_pool(conn.url)
            self._engines[conn.url] = aioredis.from_url(conn.url)

        # Return actual connection (engine)
        return self.engines[conn.url]




    # def _connection(self, connection: str = None):
    #     """Get one connection by name"""
    #     if not connection: connection = self._current_conn or self.default
    #     self._current_conn = None
    #     conn = self.connections.get(connection)
    #     if not conn:
    #         raise Exception('Redis connection {} not found'.format(connection))
    #     return conn

    # def connection(self, connection: str = None):
    #     """Change the default connection for one query"""
    #     if connection: self._current_conn = connection
    #     return self

    # async def connect(self, connection: str = None):
    #     conn = self._connection(connection)

    #     # Connect to redis if connection never started
    #     if conn.url not in self.engines:
    #         self.engines[conn.url] = await aioredis.create_redis_pool(conn.url)

    #     # Return actual connection (engine)
    #     return self.engines[conn.url]

    # async def get(self, key: Any, default: Any = None):
    #     redis = await self.connect()
    #     return await redis.get(key)

    # async def set(self, key: Any, value: Any):
    #     redis = await self.connect()
    #     return await redis.set(key, value)
