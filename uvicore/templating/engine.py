from __future__ import annotations
import uvicore
from typing import Dict, List, Any, Optional
from uvicore.support.dumper import dump, dd
from uvicore.contracts import Template as TemplateInterface

try:
    import jinja2
except ImportError:  # pragma: nocover
    jinja2 = None  # type: ignore

# This template system works for CLI templating and Web (starlette) templating
# But starlette is optional
try:
    from starlette.responses import Response
except ImportError:  # pragma: nocover
    class Response:
        pass


@uvicore.service('uvicore.templating.engine.Templates',
    aliases=['Templates', 'templates'],
    singleton=True,
)
class Templates(TemplateInterface):
    """Uvicore Template Engine"""

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

        # Only for starlette compatibility
        self.context_processors = {}

    def render(self, template_name: str, data: Optional[Dict] = {}) -> str:
        """Render a template as string (for CLI usage, not a Web response)"""
        template = self._env.get_template(template_name)
        return template.render(data)

    def render_web_response(self, name: str, context: dict, status_code: int = 200, headers: dict = None, media_type: str = None, background: BackgroundTask = None) -> _TemplateResponse:
        """Render a template as Web Response"""
        if "request" not in context:
            raise ValueError('context must include a "request" key')
        template = self._env.get_template(name)
        return _TemplateResponse(
            template,
            context,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )

    def _init(self) -> None:
        """Initialize the template engine (from bootstrap process)"""
        assert jinja2 is not None, "jinja2 is not installed"

        # Load our jinja2 environment
        loader = jinja2.FileSystemLoader(self.paths)
        self._env = jinja2.Environment(loader=loader, autoescape=True)

        # Register all user defined context processors
        self._register_context_processors()

    def _register_context_processors(self):
        """Register all user defined context processors"""
        # Add Context Functions
        for name, method in self.context_functions.items():
            #self._env.globals[name] = jinja2.contextfunction(method)
            self._env.globals[name] = jinja2.pass_context(method)
            #self._context_processors[name] = method

        # Add Context Filters
        for name, method in self.context_filters.items():
            #self._env.filters[name] = jinja2.contextfilter(method)
            self._env.filters[name] = jinja2.pass_context(method)
            #self._context_processors[name] = method

        # Add Filters
        for name, method in self.filters.items():
            self._env.filters[name] = method

        # Add Tests
        for name, method in self.tests.items():
            self._env.tests[name] = method

    def include_path(self, path) -> None:
        """Include template paths to search for"""
        if path not in self.paths:
            self._paths.append(path)

    def include_context_function(self, name: str, method: Any) -> None:
        """Include a context function"""
        self._context_functions[name] = method

    def include_context_filter(self, name: str, method: Any) -> None:
        """Include a context filter"""
        self._context_filters[name] = method

    def include_filter(self, name: str, method: Any) -> None:
        """Include a function"""
        self._filters[name] = method

    def include_test(self, name: str, method: Any) -> None:
        """Include a test"""
        self._tests[name] = method



class _TemplateResponse(Response):
    """Templated text/html Web Response"""

    media_type = "text/html"

    def __init__(
        self,
        template: typing.Any,
        context: dict,
        status_code: int = 200,
        headers: dict = None,
        media_type: str = None,
        background: BackgroundTask = None,
    ):
        self.template = template
        self.context = context
        content = template.render(context)
        super().__init__(content, status_code, headers, media_type, background)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = self.context.get("request", {})
        extensions = request.get("extensions", {})
        if "http.response.template" in extensions:
            await send(
                {
                    "type": "http.response.template",
                    "template": self.template,
                    "context": self.context,
                }
            )
        await super().__call__(scope, receive, send)
