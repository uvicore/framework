from uvicore.typing import Any, Callable
from uvicore.typing import Dict, List, Any, Union, Callable
from abc import ABC, abstractmethod, abstractproperty, abstractclassmethod


class Job(ABC, Dict):

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
        """Dispatch an async Job Class"""
        pass
