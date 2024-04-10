from abc import ABC, abstractmethod, abstractproperty
from uvicore.typing import Dict, List, Any, Union, Callable


class Dispatcher(ABC):

    @abstractproperty
    # def events(self) -> Dict[str, Dict]:
    #     """Dictionary of all registered events in uvicore and all packages"""
    #     pass

    @abstractproperty
    def listeners(self) -> Dict[str, List]:
        """Dictionary of all listeners for each event"""
        pass

    @abstractproperty
    def wildcards(self) -> List:
        """List of all wildcard listeners"""
        pass

    # @abstractmethod
    # def event(self, event: Union[str, Callable]) -> Dict:
    #     """Get one event by str name or class"""
    #     pass

    @abstractmethod
    def event_listeners(self, event: str) -> List:
        """Get all listeners for an event including wildcard, sorted by priority ASC"""
        pass

    # @abstractmethod
    # def register(self, events: Dict[str, Dict] = None, *, name: str = None, description: str = None, is_async: bool = False, dynamic: bool = True):
    #     """Register an event with the system.  Retrieve with .events property"""
    #     pass

    @abstractmethod
    def listen(self, events: Union[str, List], listener: Union[str, Callable] = None, *, priority: int = 50) -> None:
        """Append a listener (string or method) callback to one or more events"""
        pass

    def handle(self, events: Union[str, List], listener: Union[str, Callable] = None, *, priority: int = 50) -> None:
        """Alias to listen"""
        pass

    @abstractmethod
    def subscribe(self, listener: Union[str, Callable]) -> None:
        """Add a subscription class which handles both registration and listener callbacks"""
        pass

    @abstractmethod
    def dispatch(self, event: Any, payload = {}) -> None:
        """Fire off an event and run all listener callbacks"""
        pass

    @abstractmethod
    async def dispatch_async(self, event: Any, payload = {}) -> None:
        """Fire off an event and run all async listener callbacks"""
        pass

    @abstractmethod
    async def codispatch(self, event: Any, payload: Dict = {}) -> None:
        """Alias for dispatch_async()"""
        pass

