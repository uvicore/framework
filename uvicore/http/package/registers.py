import uvicore
from uvicore.support.dumper import dump, dd
from uvicore.support.module import location, load
from uvicore.typing import List, Dict, OrderedDict, Union
from uvicore.contracts import Provider
from uvicore.support.collection import unique



class Http(Provider):
    """Http Service Provider Mixin"""

    def register_http_web_routes(self, module: str, prefix: str, name_prefix: str = ''):
        # Default registration
        self.package.registers.defaults({'web_routes': True})

        # We do NOT check if package can registers.web_routes here as we always want
        # the package definition to contain the routes.  Instead we simply don't load
        # the routes in http/bootstrap.py merge_routes() if registers is False

        # Add routes to package definition
        self.package.web.routes_module = module
        self.package.web.prefix = prefix
        self.package.web.name_prefix = name_prefix

    def register_http_api_routes(self, module: str, prefix: str, name_prefix: str = 'api'):
        # Default registration
        self.package.registers.defaults({'api_routes': True})

        # We do NOT check if package can registers.api_routes here as we always want
        # the package definition to contain the routes.  Instead we simply don't load
        # the routes in http/bootstrap.py merge_routes() if registers is False

        # Add routes to package definition
        self.package.api.routes_module = module
        self.package.api.prefix = prefix
        self.package.api.name_prefix = name_prefix

    # def middlewareNO(self, items: OrderedDict):
    #     # Don't think this should be here.  middleware is app global
    #     # not per package.  I add apps middleware in http service.py
    #     # Default registration
    #     self.package.registers.defaults({'middleware': True})

    #     # Register middleware only if allowed
    #     #if self.package.registers.middleware:
    #         #self._add_http_definition('middleware', items)

    def register_http_views(self, modules: List):
        # Default registration
        self.package.registers.defaults({'views': True})

        # Register views only if allowed
        if self.package.registers.views:
            self.package.web.view_paths = modules

    def register_http_view_context_processors(self, items: Dict):
        # Default registration - template obeys view registration
        self.package.registers.defaults({'views': True})

        # Register templates only if [views] allowed
        if self.package.registers.views:
            self.package.web.context_processors = Dict(items)

    def register_http_view_composers(self, module: Union[str, Dict], views: Union[str, List] = None, *, append: bool = False):
        # Default registration - we use same 'views' registration for composers as well
        self.package.registers.defaults({'views': True})

        # Register composers only if allowed
        if self.package.registers.views:
            if type(module) == dict:
                # Dict based, example:
                # self.composers({
                #     'mreschke.themes.http.composers.theme.Theme': 'themes/*',
                #     'mreschke.themes.http.composers.theme.Theme2': ['themes/*', 'themes2/*'],
                # })
                for (mod, views) in module.items():
                    self.composers(mod, views)
            else:
                # Parameter based
                if views is None:
                    # Delete this entire view composer
                    del self.package.web.view_composers[module]
                    return
                if type(views) != list: views = [views]
                if append:
                    # Append views to this modules List
                    if not self.package.web.view_composers[module]: self.package.web.view_composers[module] = []
                    self.package.web.view_composers[module].extend(views)
                    self.package.web.view_composers[module] = unique(self.package.web.view_composers[module])
                else:
                    self.package.web.view_composers[module] = views


    def register_http_assets(self, items: List):
        # Default registration
        self.package.registers.defaults({'assets': True})

        # Register assets only if allowed
        if self.package.registers.assets:
            self.package.web.asset_paths = items

    def register_http_public(self, items: List):
        self.package.web.public_paths = items


