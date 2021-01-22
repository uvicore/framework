from uvicore.support.dumper import dump, dd
from uvicore.typing import Dict, List
from uvicore.support.module import location
from uvicore.database import Connection


class Cli:
    """CLI Service Provider Mixin"""

    def _add_cli_definition(self, key, value):
        if 'console' not in self.package:
            self.package['console'] = Dict()
        self.package['console'][key] = value

    def commands(self, items: Dict):
        # Default registration
        self.package.registers.defaults({'commands': True})

        # Register commands only if allowed
        if self.package.registers.commands:
            self._add_cli_definition('groups', Dict(items))
