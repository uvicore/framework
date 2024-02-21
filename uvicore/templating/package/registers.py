import uvicore
from uvicore.support.dumper import dump, dd
from uvicore.support.module import location, load
from uvicore.typing import List, Dict, OrderedDict, Union
from uvicore.contracts import Provider
from uvicore.support.collection import unique


class Templating(Provider):
    """Templating Provider Mixin"""

    def register_templating_paths(self, modules: List):
        # Default registration - template obeys view registration
        self.package.registers.defaults({'templates': True})

        # Register templates only if [templates] allowed
        if self.package.registers.templates:
            self.package.templating.paths = modules

    def register_templating_context_processors(self, items: Dict):
        # Default registration - template obeys view registration
        self.package.registers.defaults({'templates': True})

        # Register templates only if [templates] allowed
        if self.package.registers.templates:
            self.package.templating.context_processors = Dict(items)
