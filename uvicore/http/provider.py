from uvicore.support.dumper import dump, dd
from uvicore.support.module import location
from uvicore.typing import List, Dict

class Http:
    """Http Service Provider Mixin"""

    def _add_http_definition(self, key, value):
        if 'http' not in self.package:
            self.package['http'] = Dict()
        self.package['http'][key] = value

    def web_routes(self, module: str, prefix: str):
        # Default registration
        self.package.registers.defaults({'web_routes': True})

        # Register WEB routes only if allowed
        if self.package.registers.web_routes:
            self._add_http_definition('web_routes', module)
            self._add_http_definition('web_route_prefix', prefix)

    def api_routes(self, module: str, prefix: str):
        # Default registration
        self.package.registers.defaults({'api_routes': True})

        # Register API routes only if allowed
        if self.package.registers.api_routes:
            self._add_http_definition('api_routes', module)
            self._add_http_definition('api_route_prefix', prefix)

    def middleware(self, items: List):
        # Default registration
        self.package.registers.defaults({'middleware': True})

        # Register middleware only if allowed
        if self.package.registers.middleware:
            self._add_http_definition('middleware', items)

    def views(self, items: List):
        # Default registration
        self.package.registers.defaults({'views': True})

        # Register views only if allowed
        if self.package.registers.views:
            self._add_http_definition('view_paths', items)

    def assets(self, items: List):
        # Default registration
        self.package.registers.defaults({'assets': True})

        # Register assets only if allowed
        if self.package.registers.assets:
            self._add_http_definition('asset_paths', items)

    def template(self, items: Dict):
        # Default registration - template obeys view registration
        self.package.registers.defaults({'views': True})

        # Register templates only if [views] allowed
        if self.package.registers.views:
            self._add_http_definition('template_options', Dict(items))
