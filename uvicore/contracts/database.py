from abc import ABC, abstractmethod
from typing import Dict, List, Any, Union


class Database(ABC):
    pass

    # @property
    # @abstractmethod
    # def events(self) -> Dict: pass

    # @property
    # @abstractmethod
    # def listeners(self) -> Dict[str, List]: pass

    # @property
    # @abstractmethod
    # def wildcards(self) -> List: pass

    # @abstractmethod
    # def register(self, events: Dict):
    #     pass

    # @abstractmethod
    # def listen(self, events: Union[str, List], listener: Any) -> None:
    #     pass

    # @abstractmethod
    # def dispatch(self, event: Any, payload = {}) -> None:
    #     pass

    # @abstractmethod
    # def get_listeners(self, event: str) -> List:
    #     pass
