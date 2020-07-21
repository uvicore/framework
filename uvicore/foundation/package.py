from dataclasses import dataclass
from typing import Dict, List, NamedTuple, Optional

from uvicore.contracts import Package as PackageInterface
from uvicore.database.connection import Connection
from uvicore.support import module


class Package(PackageInterface):

    def config(self, dotkey: str = None):
        # Do NOT import config normally at the top or you get recursive import error
        # Because config is not actually ready when this file is imported
        # So we fire it up dynamically each time this is called
        Config = module.load('uvicore.config').mod
        if dotkey:
            return Config(self.config_prefix + '.' + dotkey)
        else:
            return Config(self.config_prefix)

    def connection(self, name: str = None):
        if name:
            return next(connection for connection in self.connections if connection.name == name)
        else:
            return next(connection for connection in self.connections if connection.default == True)
