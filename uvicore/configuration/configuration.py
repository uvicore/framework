import os
from typing import Any, Dict

import uvicore
from uvicore.contracts import Config as ConfigInterface
from uvicore.support import dictionary
from uvicore.support.dumper import dd, dump


class _Configuration(ConfigInterface):
    #config: Dict = {}
    @property
    def items(self) -> Dict:
        return self._items

    def __init__(self) -> None:
        self._items: Dict = {}

    def get(self, dotkey: str = None, config: Dict = None) -> Any:
        # Recursive for dot notation
        if not dotkey:
            return self.items
        if config is None: config = self.items
        if "." in dotkey:
            key, rest = dotkey.split(".", 1)
            if key not in config:
                config[key] = {}
            return self.get(rest, config[key])
        else:
            if dotkey in config:
                return config[dotkey]
            else:
                return None

    def set(self, dotkey: str, value: any, config: Dict = None) -> Any:
        # Recursive for dot notation
        # Remember objects are byRef, so changing config also changes self.items
        if config is None: config = self._items
        if "." in dotkey:
            key, rest = dotkey.split(".", 1)
            if key not in config:
                config[key] = {}
            return self.set(rest, value, config[key])
        else:
            config[dotkey] = value
            return value

    def merge(self, dotkey: str, value: Any) -> None:
        existing = self.get(dotkey);
        if not existing:
            return self.set(dotkey, value)
        else:
            # Perform deep merge on existing config
            # This overrides 'existing' data with 'value' data
            # And updates 'existing' with merged vlues
            dictionary.deep_merge(value, existing)

            # Finally set the new merged config
            self.set(dotkey, existing)

    def __call__(self, dotkey: str = None):
        return self.get(dotkey)

# IoC Class Instance
# NO - Circular issues on override
#Configuration: ConfigInterface = uvicore.ioc.make('Config')

# Public API for import * and doc gens
__all__ = ['_Configuration']
