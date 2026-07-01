from abc import ABC, abstractmethod
from typing import List, Any, Callable
from uvicore.typing import Dict


class Dispatcher(ABC):

    # @property
    # @abstractmethod
    # def events(self) -> Dict[str, Dict]:
    #     """Dictionary of all registered events in uvicore and all packages"""
    #     pass

    @property
    @abstractmethod
    def listeners(self) -> Dict[str, List]:
        """Dictionary of all listeners for each event"""
        pass

    @property
    @abstractmethod
    def wildcards(self) -> List:
        """List of all wildcard listeners"""
        pass

    @property
    @abstractmethod
    def registered_events(self) -> List:
        """Get all registered events from IOC bindings and manual registrations"""
        pass

    @property
    @abstractmethod
    def expanded_sorted_listeners(self) -> List:
        """Get all listeners with expanded wildcards, sorted by priority ASC"""
        pass

    # @abstractmethod
    # def event(self, event: Union[str, Callable]) -> Dict:
    #     """Get one known (pre-registered) EventInfo by str name or class"""
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
    def listen(self, events: str | List, listener: str | Callable = None, *, priority: int = 50) -> None:
        """Decorator or method to append a listener (string or Callable) callback to one or more events."""
        pass

    @abstractmethod
    def listener(self, events: str | List, listener: str | Callable = None, *, priority: int = 50) -> None:
        """Decorator or method to append a listener (string or Callable) callback to one or more events.  Alias to listen()."""
        pass

    @abstractmethod
    def handle(self, events: str | List, listener: str | Callable = None, *, priority: int = 50) -> None:
        """Decorator or method to append a listener (string or Callable) callback to one or more events.  Alias to listen()."""
        pass

    @abstractmethod
    def handler(self, events: str | List, listener: str | Callable = None, *, priority: int = 50) -> None:
        """Decorator or method to append a listener (string or Callable) callback to one or more events.  Alias to listen()."""
        pass

    @abstractmethod
    def call(self, events: str | List, listener: str | Callable = None, *, priority: int = 50) -> None:
        """Decorator or method to append a listener (string or Callable) callback to one or more events.  Alias to listen()."""
        pass

    @abstractmethod
    def subscribe(self, listener: str | Callable) -> None:
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

