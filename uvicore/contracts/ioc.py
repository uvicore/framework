from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, TypeVar

T = TypeVar('T')


@dataclass
class Binding(ABC):
    path: Optional[str]
    object: Optional[Any]
    instance: Optional[Any]
    type: Optional[str]
    factory: Optional[Any]
    kwargs: Optional[Dict]
    singleton: bool
    aliases: List


class Ioc(ABC):
    @property
    @staticmethod
    def bindings(self) -> Dict[str, Binding]:
        pass

    @property
    @staticmethod
    def aliases(self) -> Dict[str, str]:
        pass

    # @abstractmethod
    # def config(self, config: Dict) -> None:
    #     """Set the main running app config dictionary for IoC binding override configs"""
    #     pass

    @abstractmethod
    def binding(self, name: str) -> Binding:
        """Get an IoC binding object by name or alias"""
        pass

    @abstractmethod
    def make(self, name: str, default: Callable[[], T] = None, **kwargs) -> T:
        """Make a module/class/method by name or alias from IoC bindings"""
        pass

    @abstractmethod
    def bind(self, name: str, object: Any, *, factory: Any = None, kwargs: Dict = None, singleton: bool = False, aliases: List = []) -> None:
        """Add an IoC binding"""
        pass

    @abstractmethod
    def bind_map(self, mapping: Dict[str, Dict]) -> None:
        """Add IoC bindings from dictionary"""
        pass

    @abstractmethod
    def alias(self, src: str, dest: str) -> None:
        """Add alias to existing binding"""
        pass
