import uvicore
from uvicore.contracts import Package as PackageInterface
from typing import Dict, List, NamedTuple, Any
from uvicore.contracts import Connection
from uvicore.types import Dic


# @uvicore.service(aliases=['Package', 'package'])
# class Package(PackageInterface):

#     def config(self, dotkey: str = None):
#         if dotkey:
#             return uvicore.config(self.name + '.' + dotkey)
#         else:
#             return uvicore.config(self.name)

#     def connection(self, name: str = None):
#         if name:
#             return next(connection for connection in self.connections if connection.name == name)
#         else:
#             #return next(connection for connection in self.connections if connection.default == True)
#             if 'database' in self.config():
#                 return next(connection for connection in self.connections if connection.name == self.config('database.default'))



@uvicore.service(aliases=['Package', 'package'])
class Package(Dic):

    def config(self, dotkey: str = None) -> Any:
        if dotkey:
            return uvicore.config(self.name + '.' + dotkey)
        else:
            return uvicore.config(self.name)

    def connection(self, name: str = None) -> Connection:
        if not self.database.connections: return None
        if name:
            return next(connection for connection in self.database.connections if connection.name == name)
        else:
            return next(connection for connection in self.database.connections if connection.name == self.database.connection_default)
            #if 'database' in self.config():
            #    return next(connection for connection in self.connections if connection.name == self.config('database.default'))








# IoC Class Instance
# No because not to be used by the public
#Package: _Package = uvicore.ioc.make('Package', _Package, aliases=['package'])

# Public API for import * and doc gens
#__all__ = ['_Package']
