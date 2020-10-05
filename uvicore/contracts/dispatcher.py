from abc import ABC, abstractmethod
from typing import Dict, List, Any, Union, Callable


class Dispatcher(ABC):

    @property
    @abstractmethod
    def events(self) -> Dict[str, Dict]:
        """Dictionary of all registered events in uvicore and all packages"""
        pass

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

    @abstractmethod
    def register(self, events: Dict[str, Dict]):
        """Register an event with the system.  Retrieve with .events property"""
        pass

    @abstractmethod
    def listen(self, events: Union[str, List], listener: Union[str, Callable]) -> None:
        """Append a listener (string or method) callback to one or more events"""
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
    def event(self, event: Union[str, Callable]) -> Dict:
        """Get one event by str name or class"""
        pass

    @abstractmethod
    def event_listeners(self, event: str) -> List:
        """Get all listeners for an event including wildcard"""
        pass
