from uvicore.support.dumper import dump, dd
from uvicore.support.collection import Dic
from uvicore.support.module import location
from uvicore.database import Connection
from typing import Dict, List


class Cli:
    """CLI Service Provider Mixin"""

    def _add_cli_definition(self, key, value):
        if 'console' not in self.package:
            self.package['console'] = Dic()
        self.package['console'][key] = value

    def commands(self, items: Dict):
        # Default registration
        self.package.registers.defaults({'commands': True})

        # Register commands only if allowed
        if self.package.registers.commands:
            self._add_cli_definition('groups', Dic(items))
