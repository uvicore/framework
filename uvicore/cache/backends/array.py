import pickle

import uvicore
from time import time
from uvicore.typing import Dict, Any, Callable, Union, List, Tuple
from uvicore.support.dumper import dump, dd
from uvicore.contracts import Cache as CacheInterface
from uvicore.cache.manager import Manager

@uvicore.service()
class Array(CacheInterface):
    def __init__(self, manager: Manager, store: Dict):
        self.manager = manager
        self.prefix = store.prefix
        self.seconds = store.seconds
        self.items = {}
        self.items_ttl = {}

    def connect(self, store: str = None) -> CacheInterface:
        """Connect to a cache backend store"""
        return self.manager.connect(store)

    def store(self, store: str = None) -> CacheInterface:
        """Alias to connect"""
        return self.connect(store)

    async def has(self, key: str) -> bool:
        """Check if key exists"""
        key = self._prepair(key)
        return key in self.items.keys()

    async def get(self, key: Union[str, List], *, default: Any = None) -> Any:
        """Get one or more key values if exists else return default value"""
        keys = self._prepair(key)
        if type(keys) == list:
            values = Dict()
            for key in keys:
                return_key = key[len(self.prefix):]
                if self._has(key):
                    # Item exists, get it
                    values[return_key] = self._deserialize(self.items[key])
                else:
                    # Item does not exist, set default
                    values[return_key] = default
            return values
        else:
            if self._has(keys):
                # Item exists, get it
                return self._deserialize(self.items[keys])
            else:
                # Item does not exist, set default
                return default

    async def remember(self, key: Union[str, Dict], callback: Union[Callable, Any] = None, *, seconds: int = None) -> Any:
        """Get a key if exists, if not SET the key to callback value"""
        keys = self._prepair(key)
        if type(key) != dict: keys = {keys:callback}
        value = {}
        for key, callback in keys.items():
            if self._has(key):
                # Item exists, simply return value
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
        keys = self._prepair(key)
        if seconds is None: seconds = self.seconds
        if type(keys) != dict: keys = {keys:value}
        for (key, value) in keys.items():
            self.items[key] = self._serialize(value)
            if seconds == 0 and key in self.items_ttl:
                del self.items_ttl[key]
            elif seconds > 0:
                self.items_ttl[key] = self._now() + seconds

    async def pull(self, key: Union[str, Dict]) -> Any:
        """Get one or more key values from cache them remove them after"""
        keys = self._prepair(key)
        value = await self.get(key)
        await self.forget(keys)
        return value

    async def add(self, key: str, value: Any, *, seconds: int = None) -> bool:
        """Put a single value in cache only if not exists"""
        key = self._prepair(key)
        if self._has(key):
            # Item already exists, return False for NOT added
            return False
        else:
            # Item does not exist, set value and return True
            await self.put(key, value)
            return True

    async def touch(self, key: str, *, seconds: int = None) -> bool:
        """Touch a key, if seconds are provided, also reset expire TTL"""
        key = self._prepair(key)
        if seconds is None: seconds = self.seconds
        if self._has(key) and seconds is not None:
            self.items_ttl[key] = self._now() + seconds
            return True
        return False

    async def increment(self, key, by: int = 1, *, seconds: int = None) -> int:
        """Increment a key by integer specified.  If key not exists, sets key to increment value"""
        key = self._prepair(key)
        if seconds is None: seconds = self.seconds
        value = 0
        if self._has(key): value = await self.get(key)
        if type(value) == int:
            value += 1
            self.put(key, value, seconds=seconds)
        return value

    async def decrement(self, key, by: int = 1, *, seconds: int = None) -> int:
        """Decrement a key by integer specified.  If key not exists, sets key to decrement value"""
        key = self._prepair(key)
        if seconds is None: seconds = self.seconds
        value = 0
        if self._has(key): value = await self.get(key)
        if type(value) == int:
            value -= 1
            self.put(key, value, seconds=seconds)
        return value

    async def forget(self, key: Union[str, List]) -> None:
        """Delete a key from cache"""
        keys = self._prepair(key)
        if type(keys) != list: keys = [keys]
        for key in keys:
            if key in self.items:
                del self.items[key]
            if key in self.items_ttl:
                del self.items_ttl[key]

    async def flush(self) -> None:
        """Flush entire cache.  Only deletes keys with proper cache prefix."""
        delete = []
        for key in self.items.keys():
            if self.prefix in key:
                delete.append(key)
        for key in delete:
            del self.items[key]

    def _has(self, key: str) -> bool:
        # This is an internal _has() only.  Why?  Because the public facing
        # has is async def.  But it doesn't need to be.  Need to keep public
        # as async def to match interface as Redis and other backends must be
        # async def.

        # I don't use _prepair here because ._has() is often used
        # by many other internal method here.  Which means _prepair and therefore
        # _expire() will be called many times.  So instead I just deduce
        # the prefix right here.  This is only OK because _has() is INTERNAL
        # and all callers already check _expire through their _prepair call.
        # The public facing has() must use _prepair and therefore _expire or you
        # could say a key exists even if its technically expired.
        key = str(key)
        prefix = self.prefix
        if len(key) > len(prefix) and key[0:len(prefix)] == prefix: prefix = ''
        return (prefix + key) in self.items.keys()

    def _prepair(self, key: Union[str, List] = None) -> Union[str, List, Dict]:
        if key:
            if type(key) == list:
                # Check if prefix already added
                key0 = str(key[0])
                prefix = self.prefix
                if len(key0) > len(prefix) and key0[0:len(prefix)] == prefix: prefix = ''
                keys = [prefix + k for k in key]
                for k in keys:
                    self._expire(k)
                return keys
            elif type(key) == dict:
                key0 = [x for x in key.keys()][0]
                prefix = self.prefix
                if len(key0) > len(prefix) and key0[0:len(prefix)] == prefix: prefix = ''
                for k in key.keys():
                    self._expire(prefix + k)
                return {prefix + k:v for k,v in key.items()}
            else:
                # Check if prefix already added
                key = str(key)
                prefix = self.prefix
                if len(key) > len(prefix) and key[0:len(prefix)] == prefix: prefix = ''
                self._expire(prefix + key)
                return prefix + key
        else:
            return None

    def _expire(self, key):
        """Delete keys that are expired anytime they are accessed"""
        # If entry not in self.items_ttl, it never expires, keep it forever
        if key in self.items_ttl:
            if key in self.items.keys():
                now = self._now()
                if now >= self.items_ttl[key]:
                    del self.items[key]
                    del self.items_ttl[key]

    def _now(self) -> int:
         return int(time())

    def _serialize(self, value):
        return value
        #return pickle.dumps(value)

    def _deserialize(self, value):
        # Error here means value was never serialized.
        # Like with .increment and .decrement keys
        return value
        # try:
        #     return pickle.loads(value)
        # except:
        #     return value.decode()

