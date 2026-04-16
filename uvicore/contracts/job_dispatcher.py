from uvicore.typing import Any
from abc import ABC, abstractmethod


class JobDispatcher(ABC):

    @abstractmethod
    def dispatch(self, instance: object) -> Any:
        """Dispatch a Job Class"""
        pass

    @abstractmethod
    async def dispatch_async(self, instance: object) -> Any:
        """Dispatch an async Job Class"""
        pass

    @abstractmethod
    async def codispatch(self, instance: object) -> Any:
        """Alias for dispatch_async()"""
        pass

