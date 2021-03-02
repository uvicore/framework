import uvicore
from uvicore.support.dumper import dump, dd
from uvicore.support.module import location, load
from uvicore.typing import List, Dict, OrderedDict
from uvicore.contracts import Provider
from uvicore.console import command_is


class Http(Provider):
    """Http Service Provider Mixin"""

    def web_routes(self, module: str, prefix: str, name_prefix: str = ''):
        # Default registration
        self.package.registers.defaults({'web_routes': True})

        # Allow only if running as HTTP or from certain CLI commands like package list/show...
        # if self.package.registers.web_routes and (
        #     uvicore.app.is_http or
        #     command_is('http') or
        #     command_is('package')
        # ) == False: return

        self.package.web.routes_module = module
        self.package.web.prefix = prefix
        self.package.web.name_prefix = name_prefix

        # # Import main web routes module
        # routes = load(module).object(self.package)

        # # Get name prefix from package name plus custom name prefix
        # if name_prefix:
        #     if name_prefix[0] == '.': name_prefix = name_prefix[1:]
        #     name_prefix = self.package.name + '.' + name_prefix
        # else:
        #     name_prefix = self.package.name

        # # Import the web router and create a new instance
        # from uvicore.http.routing.web_router import WebRouter  # isort:skip
        # router = WebRouter(self.package, prefix, name_prefix)

        # # Get returned router with all defined routes
        # router = routes.register(router)

        # # Merge routes into package definition
        # self.package.web.routes.merge(router.routes)

    def api_routes(self, module: str, prefix: str, name_prefix: str = 'api'):
        # Default registration
        self.package.registers.defaults({'api_routes': True})

        # Allow only if running as HTTP or from certain CLI commands like package list/show...
        # if self.package.registers.web_routes and (
        #     uvicore.app.is_http or
        #     command_is('http') or
        #     command_is('package')
        # ) == False: return

        self.package.api.routes_module = module
        self.package.api.prefix = prefix
        self.package.api.name_prefix = name_prefix

        # # Import main web routes module
        # routes = load(module).object(self.package)

        # # Get name prefix from package name plus custom name prefix
        # if name_prefix:
        #     if name_prefix[0] == '.': name_prefix = name_prefix[1:]
        #     name_prefix = self.package.name + '.' + name_prefix
        # else:
        #     name_prefix = self.package.name

        # # Import the web router and create a new instance
        # from uvicore.http.routing.api_router import ApiRouter  # isort:skip
        # router = ApiRouter(self.package, prefix, name_prefix)

        # # Get returned router with all defined routes
        # router = routes.register(router)

        # # Merge routes into package definition
        # self.package.api.routes.merge(router.routes)

    def middlewareNO(self, items: OrderedDict):
        # Don't think this should be here.  middleware is app global
        # not per package.  I add apps middleware in http service.py
        # Default registration
        self.package.registers.defaults({'middleware': True})

        # Register middleware only if allowed
        #if self.package.registers.middleware:
            #self._add_http_definition('middleware', items)

    def views(self, items: List):
        # Default registration
        self.package.registers.defaults({'views': True})

        # Register views only if allowed
        if self.package.registers.views:
            self.package.web.view_paths = items

    def assets(self, items: List):
        # Default registration
        self.package.registers.defaults({'assets': True})

        # Register assets only if allowed
        if self.package.registers.assets:
            self.package.web.asset_paths = items

    def public(self, items: List):
        self.package.web.public_paths = items


    def template(self, items: Dict):
        # Default registration - template obeys view registration
        self.package.registers.defaults({'views': True})

        # Register templates only if [views] allowed
        if self.package.registers.views:
            self.package.web.template_options = Dict(items)
