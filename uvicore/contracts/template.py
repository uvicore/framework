from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


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

    @property
    @abstractmethod
    def context_filters(self) -> Dict: pass

    @property
    @abstractmethod
    def filters(self) -> Dict: pass

    @property
    @abstractmethod
    def tests(self) -> Dict: pass

    def render(self, template_name: str, data: Optional[Dict] = {}) -> str:
        """Render a template as string (for CLI usage, not a Web response)"""
        pass

    def render_web_response(self, name: str, context: dict, status_code: int = 200, headers: dict = None, media_type: str = None, background = None):
        """Render a template as Web Response"""
        pass
