import jinja2
from typing import Dict, List, Any
from starlette.templating import Jinja2Templates as _Jinja2Templates
from uvicore.support.dumper import dump, dd
from uvicore.contracts import Template as TemplateInterface


class Jinja(TemplateInterface, _Jinja2Templates):

    env: jinja2.Environment = None
    paths: List[str] = []
    context_functions: Dict = {}
    context_filters: Dict = {}
    filters: Dict = {}
    tests: Dict = {}

    def __init__(self) -> None:
        pass

    def init(self) -> None:
        # Load our jinja2 environment
        loader = jinja2.FileSystemLoader(self.paths)
        self.env = jinja2.Environment(loader=loader, autoescape=True)

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
            self.env.globals[name] = jinja2.contextfunction(method)

        # Add Context Filters
        for name, method in self.context_filters.items():
            self.env.filters[name] = jinja2.contextfilter(method)

        # Add Filters
        for name, method in self.filters.items():
            self.env.filters[name] = method

        # Add Tests
        for name, method in self.tests.items():
            self.env.tests[name] = method

        # # Add jinja options defined in packages service providers
        # for options in self.options.values():
        #     if 'globals' in options:
        #         for g in options['globals']:
        #             self.env.globals[g['name']] = jinja2.contextfunction(g['method'])
        #     if 'filters' in options:
        #         for f in options['filters']:
        #             self.env.filters[f['name']] = f['method']
        #     if 'context_filters' in options:
        #         for f in options['context_filters']:
        #             self.env.filters[f['name']] = jinja2.contextfilter(f['method'])
        #     if 'tests' in options:
        #         for t in options['tests']:
        #             self.env.tests[t['name']] = t['method']

    def include_path(self, path) -> None:
        if path not in self.paths:
            self.paths.append(path)

    def include_context_function(self, name: str, method: Any) -> None:
        self.context_functions[name] = method

    def include_context_filter(self, name: str, method: Any) -> None:
        self.context_filters[name] = method

    def include_filter(self, name: str, method: Any) -> None:
        self.filters[name] = method

    def include_test(self, name: str, method: Any) -> None:
        self.tests[name] = method
