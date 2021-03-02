from abc import ABC, abstractmethod
from dataclasses import dataclass
from uvicore.typing import Any, Callable, Dict, List, Optional, TypeVar, Union

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
    def binding(self, name: str = None, *, type: str = None, include_overrides: bool = True) -> Union[Binding, Dict]:
        """Get an IoC binding object by name or alias"""
        pass

    @abstractmethod
    def make(self, name: str, default: Callable[[], T] = None, **kwargs) -> T:
        """Make a module/class/method by name or alias from IoC bindings"""
        pass

    @abstractmethod
    def bind_from_decorator(self, cls, name: str = None, *, object_type: str = None, factory: Any = None, kwargs: Dict = None, singleton: bool = False, aliases: List = []) -> None:
        """Bind from a decorator"""
        pass

    @abstractmethod
    def bind_override(self, name: str, object: str):
        """Add a binding override to an array to check later"""
        pass

    @abstractmethod
    def bind(self, name: str = None, object: Any = None, *, object_type: str = 'service', override: bool = True, factory: Any = None, kwargs: Dict = None, singleton: bool = False, aliases: List = []) -> None:
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
