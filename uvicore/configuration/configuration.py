import uvicore
from uvicore.support.dumper import dd, dump
from uvicore.contracts import Config as ConfigInterface


@uvicore.service('uvicore.configuration.configuration.Configuration',
    aliases=['Configuration', 'Config', 'configuration', 'config'],
    singleton=True,
)
class Configuration(ConfigInterface):
    pass










# OBSOLETE, now SuperDict!

import os
from typing import Any, Dict
from uvicore.support.dictionary import deep_merge
class _ConfigurationOBSOLETE(ConfigInterface):
    """Configuration private class.

    Do not import from this location.
    Use the uvicore.config singleton global instead."""

    #config: Dict = {}
    @property
    def items(self) -> Dict[str, Dict]:
        return self._items

    def __init__(self) -> None:
        self._items: Dict = {}

    def __call__(self, dotkey: str = None):
        return self.get(dotkey)

    def get(self, dotkey: str = None, _recursive_config: Dict = None) -> Any:
        # Recursive for dot notation
        if not dotkey:
            return self.items
        if _recursive_config is None: _recursive_config = self.items
        if "." in dotkey:
            key, rest = dotkey.split(".", 1)
            if key not in _recursive_config:
                _recursive_config[key] = {}
            return self.get(rest, _recursive_config[key])
        else:
            if dotkey in _recursive_config:
                return _recursive_config[dotkey]
            else:
                return None

    def set(self, dotkey: str, value: any, _recursive_config: Dict = None) -> Any:
        # Recursive for dot notation
        # Remember objects are byRef, so changing config also changes self.items
        if _recursive_config is None: _recursive_config = self._items
        if "." in dotkey:
            key, rest = dotkey.split(".", 1)
            if key not in _recursive_config:
                _recursive_config[key] = {}
            return self.set(rest, value, _recursive_config[key])
        else:
            _recursive_config[dotkey] = value
            return value

    def merge(self, dotkey: str, value: Any) -> None:
        existing = self.get(dotkey);
        if not existing:
            return self.set(dotkey, value)
        else:
            # Perform deep merge on existing config
            # This overrides 'existing' data with 'value' data
            # And updates 'existing' with merged vlues
            existing = deep_merge(value, existing)

            # Finally set the new merged config
            self.set(dotkey, existing)


# IoC Class Instance
# Not to be imported by the public from here.
# Use the uvicore.config singleton global instead.

# Public API for import * and doc gens
#__all__ = ['_Configuration']
