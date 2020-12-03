import uvicore
from uvicore.contracts import Package as PackageInterface

from dataclasses import dataclass
from typing import Dict, List, NamedTuple
from uvicore.contracts import Connection


@uvicore.service(aliases=['Package', 'package'])
class Package(PackageInterface):

    def config(self, dotkey: str = None):
        if dotkey:
            return uvicore.config(self.name + '.' + dotkey)
        else:
            return uvicore.config(self.name)

    def connection(self, name: str = None):
        if name:
            return next(connection for connection in self.connections if connection.name == name)
        else:
            #return next(connection for connection in self.connections if connection.default == True)
            if 'database' in self.config():
                return next(connection for connection in self.connections if connection.name == self.config('database.default'))


# IoC Class Instance
# No because not to be used by the public
#Package: _Package = uvicore.ioc.make('Package', _Package, aliases=['package'])

# Public API for import * and doc gens
#__all__ = ['_Package']
