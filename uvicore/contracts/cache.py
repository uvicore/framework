from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any

class Cache(ABC):

    @abstractmethod
    def connect(self, store: str = None) -> Cache:
        """Connect to a cache backend store"""

    @abstractmethod
    def store(self, store: str = None) -> Cache:
        """Alias to connect"""

    @abstractmethod
    async def has(self, key: str) -> bool:
        """Check if key exists"""

    @abstractmethod
    async def get(self, key: Union[str, List], *, default: Any = None) -> Any:
        """Get one or more key values if exists else return default value"""

    @abstractmethod
    async def remember(self, key: str, callback: Callable, *, seconds: int = 0) -> Any:
        """Get a key if exists, if not SET the key to callback value"""

    @abstractmethod
    async def put(self, key: Union[str, Dict], value: Any = None, *, seconds: int = 0) -> None:
        """Put one or more key/values in cache with optional expire in seconds (0=never expire)"""

    @abstractmethod
    async def pull(self, key: str) -> Any:
        """Get a value from cache them remove it"""

    @abstractmethod
    async def add(self, key: str, value: Any, *, seconds: int = 0) -> bool:
        """Put a single value in cache only if not exists"""

    @abstractmethod
    async def touch(self, key: str, *, seconds: int = None) -> bool:
        """Touch a key, if seconds are provided, also reset expire TTL"""

    @abstractmethod
    async def increment(self, key, by: int = 1, *, seconds: int = None) -> int:
        """Increment a key by integer specified.  If key not exists, sets key to increment"""

    @abstractmethod
    async def decrement(self, key, by: int = 1, *, seconds: int = None) -> int:
        """Decrement a key by integer specified.  If key not exists, sets key to decrement value"""

    @abstractmethod
    async def forget(self, key: str) -> None:
        """Delete a key from cache"""

    @abstractmethod
    async def flush(self) -> None:
        """Flush entire cache.  Only deletes keys with proper cache prefix."""
