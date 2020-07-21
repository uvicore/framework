from abc import ABC, abstractmethod
from typing import Dict, List, Any

class Template(ABC):

    @property
    @abstractmethod
    def env(self) -> Any: pass

    @property
    @abstractmethod
    def paths(self) -> List[str]: pass

    @property
    @abstractmethod
    def context_functions(self) -> Dict: pass
