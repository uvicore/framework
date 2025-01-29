import pickle
import uvicore
from uvicore.typing import Dict, Any, Callable, Union, List, Tuple
from uvicore.support.dumper import dump, dd
from uvicore.redis import Redis as RedisDb
from aioredis import Redis as RedisInterface
from uvicore.contracts import Cache as CacheInterface
from uvicore.cache.manager import Manager


@uvicore.service()
class Redis(CacheInterface):

    def __init__(self, manager: Manager, store: Dict):
        self.manager = manager
        self.connection = store.connection
        self.prefix = store.prefix
        self.seconds = store.seconds
        self._redis = None

    def connect(self, store: str = None) -> CacheInterface:
        """Connect to a cache backend store"""
        return self.manager.connect(store)

    def store(self, store: str = None) -> CacheInterface:
        """Alias to connect"""
        return self.connect(store)

    async def has(self, key: str) -> bool:
        """Check if key exists"""
        (redis, key) = await self._prepair(key)
        return bool(await redis.exists(key))

    async def get(self, key: Union[str, List], *, default: Any = None) -> Any:
        """Get one or more key values if exists else return default value"""
        (redis, keys) = await self._prepair(key)
        if type(keys) == list:
            values = Dict()
            for key in keys:
                return_key = key[len(self.prefix):]
                if await self.has(key):
                    # Item exists, get from redis
                    values[return_key] = self._deserialize(await redis.get(key))
                else:
                    # Item does not exist, set default
                    values[return_key] = default
            return values
        else:
            if await self.has(keys):
                # Item exists, get from redis
                return self._deserialize(await redis.get(keys))
            else:
                # Item does not exist, set default
                return default

    async def remember(self, key: Union[str, Dict], callback: Union[Callable, Any] = None, *, seconds: int = None) -> Any:
        """Get a key if exists, if not SET the key to callback value"""
        (redis, keys) = await self._prepair(key)
        if type(key) != dict: keys = {keys:callback}
        value = {}
        for key, callback in keys.items():
            if await self.has(key):
                # Item exists, simply return value
                #value[key] = await redis.get(key)
                value[key] = await self.get(key)
            else:
                # Item does not exist, set value based on callback return
                if callable(callback):
                    value[key] = await callback()
                else:
                    value[key] = callback
                await self.put(key, value[key], seconds=seconds)

        if type(key) != dict:
            # Single key, single return
            return value[key]

        # Dict key, dict return
        return value

    async def put(self, key: Union[str, Dict], value: Any = None, *, seconds: int = None) -> None:
        """Put one or more key/values in cache with optional expire in seconds (0=never expire)"""
        (redis, keys) = await self._prepair(key)
        if seconds is None: seconds = self.seconds
        if type(keys) != dict: keys = {keys:value}
        for (key, value) in keys.items():
            await redis.set(key, self._serialize(value), ex=seconds)

    async def pull(self, key: Union[str, Dict]) -> Any:
        """Get one or more key values from cache them remove them after"""
        (redis, keys) = await self._prepair(key)
        value = await self.get(key)
        await self.forget(keys)
        return value

    async def add(self, key: str, value: Any, *, seconds: int = None) -> bool:
        """Put a single value in cache only if not exists"""
        (redis, key) = await self._prepair(key)
        if await self.has(key):
            # Item already exists, return False for NOT added
            return False
        else:
            # Item does not exist, set value and return True
            await self.put(key, value, seconds=seconds)
            return True

    async def touch(self, key: str, *, seconds: int = None) -> bool:
        """Touch a key, if seconds are provided, also reset expire TTL"""
        (redis, key) = await self._prepair(key)
        if await self.has(key):
            await redis.touch(key)
            if seconds is not None:
                await redis.expire(key, seconds)
            return True
        return False

    async def increment(self, key, by: int = 1, *, seconds: int = None) -> int:
        """Increment a key by integer specified.  If key not exists, sets key to increment value"""
        (redis, key) = await self._prepair(key)
        if seconds is None: seconds = self.seconds
        await redis.incrby(key, by)
        if seconds == 0:
            # 0 means never expire
            await redis.persist(key)
        else:
            await redis.expire(key, seconds)
        return int(await redis.get(key))

    async def decrement(self, key, by: int = 1, *, seconds: int = None) -> int:
        """Decrement a key by integer specified.  If key not exists, sets key to decrement value"""
        (redis, key) = await self._prepair(key)
        if seconds is None: seconds = self.seconds
        await redis.decrby(key, by)
        if seconds == 0:
            # 0 means never expire
            await redis.persist(key)
        else:
            await redis.expire(key, seconds)
        return int(await redis.get(key))

    async def forget(self, key: Union[str, List]) -> None:
        """Delete a key from cache"""
        (redis, keys) = await self._prepair(key)
        if type(keys) != list: keys = [keys]
        await redis.delete(*keys)

    async def flush(self) -> None:
        """Flush entire cache.  Only deletes keys with proper cache prefix."""
        redis = (await self._prepair())[0]
        keys = await redis.keys(self.prefix + '*')
        await redis.delete(*keys)

    async def _prepair(self, key: Union[str, List] = None) -> Tuple[RedisInterface, Union[str, List, Dict]]:
        # Connect to redis pool if not connected
        if not self._redis:
            # RedisDB is uvicore.redis.redis.py abstraction and .connect() there
            # runs the await aioredis.create_redis_pool if not connected
            self._redis = await RedisDb.connect(self.connection)

        if key:
            if type(key) == list:
                # Check if prefix already added
                key0 = str(key[0])
                prefix = self.prefix
                if len(key0) > len(prefix) and key0[0:len(prefix)] == prefix: prefix = ''
                return (self._redis, [prefix + k for k in key])
            elif type(key) == dict:
                key0 = [x for x in key.keys()][0]
                prefix = self.prefix
                if len(key0) > len(prefix) and key0[0:len(prefix)] == prefix: prefix = ''
                return (self._redis, {prefix + k:v for k,v in key.items()})
            else:
                # Check if prefix already added
                key = str(key)
                prefix = self.prefix
                if len(key) > len(prefix) and key[0:len(prefix)] == prefix: prefix = ''
                return (self._redis, prefix + key)
        else:
            return (self._redis, None)

    def _serialize(self, value):
        return pickle.dumps(value)

    def _deserialize(self, value):
        # Error here means value was never serialized.
        # Like with .increment and .decrement keys
        try:
            return pickle.loads(value)
        except:
            return value.decode()

