import jinja2
import uvicore
from typing import Dict, List, Any
from starlette.templating import Jinja2Templates as _Jinja2Templates
from uvicore.support.dumper import dump, dd
from uvicore.contracts import Template as TemplateInterface


@uvicore.service('uvicore.http.templating.jinja._Jinja',
    aliases=['Templates', 'templates'],
    singleton=True,
)
class _Jinja(TemplateInterface, _Jinja2Templates):
    """Jinja Template private class.

    Dont access templates directly.
    Use reponse.View() instead helper instead."""

    @property
    def env(self) -> jinja2.Environment:
        return self._env

    @property
    def paths(self) -> List[str]:
        return self._paths

    @property
    def context_functions(self) -> Dict:
        return self._context_functions

    @property
    def context_filters(self) -> Dict:
        return self._context_filters

    @property
    def filters(self) -> Dict:
        return self._filters

    @property
    def tests(self) -> Dict:
        return self._tests

    def __init__(self) -> None:
        self._env = None
        self._paths = []
        self._context_functions = {}
        self._context_filters = {}
        self._filters = {}
        self._tests = {}

    def init(self) -> None:
        # Load our jinja2 environment
        loader = jinja2.FileSystemLoader(self.paths)
        self._env = jinja2.Environment(loader=loader, autoescape=True)

        # Define our own uvicore built-in options
        self._define_context_functions()

        # Add user defined options
        self._register_options()

    def _define_context_functions(self):
        def url(context: dict, name: str, **path_params: Any) -> str:
            request = context["request"]
            return request.url_for(name, **path_params)

        self.include_context_function('url', url)

    def _register_options(self):
        # Add Context Functions
        for name, method in self.context_functions.items():
            self._env.globals[name] = jinja2.contextfunction(method)

        # Add Context Filters
        for name, method in self.context_filters.items():
            self._env.filters[name] = jinja2.contextfilter(method)

        # Add Filters
        for name, method in self.filters.items():
            self._env.filters[name] = method

        # Add Tests
        for name, method in self.tests.items():
            self._env.tests[name] = method

    def include_path(self, path) -> None:
        if path not in self.paths:
            self._paths.append(path)

    def include_context_function(self, name: str, method: Any) -> None:
        self._context_functions[name] = method

    def include_context_filter(self, name: str, method: Any) -> None:
        self._context_filters[name] = method

    def include_filter(self, name: str, method: Any) -> None:
        self._filters[name] = method

    def include_test(self, name: str, method: Any) -> None:
        self._tests[name] = method


# IoC Class Instance
# No, not to be used by public by importing.  Use ioc.make instead.


# Public API for import * and doc gens
#__all__ = ['_Jinja']
