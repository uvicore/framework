import os
import uvicore
from uvicore.typing import Dict, Any
from uvicore.contracts import Connection
from uvicore.support.dumper import dump, dd
from uvicore.contracts import Package as PackageInterface


@uvicore.service(aliases=['Package', 'package'])
class Package(PackageInterface):

    @property
    def config(self) -> Dict:
        """Helper to access this packages configs"""
        return uvicore.config.dotget(self.name)

    # def config(self, dotkey: str = None) -> Any:
    #     """Helper to access this packages configs"""
    #     if dotkey:
    #         return uvicore.config(self.name + '.' + dotkey)
    #     else:
    #         return uvicore.config(self.name)

    def connection(self, name: str = None) -> Connection:
        """Helper to access this packages connections"""
        try:
            if not self.database.connections: return None
            if name:
                return next(connection for connection in self.database.connections if connection.name == name)
            else:
                return next(connection for connection in self.database.connections if connection.name == self.database.connection_default)
        except:
            return None

    def folder_path(self, key: str) -> str:
        """Get a path for a package folder, accounting for package config paths overrides"""

        # Default paths
        defaults = Dict({
            #'base': base,
            'commands': 'commands',
            'config': 'config',
            'database': 'database',
            'migrations': 'database/migrations',
            'seeders': 'database/seeders',
            'tables': 'database/tables',
            'events': 'events',
            'http': 'http',
            'api': 'http/api',
            'assets': 'http/assets',
            'controllers': 'http/controllers',
            'routes': 'http/routes',
            'static': 'http/static',
            'views': 'http/views',
            'view_composers': 'http/composers',
            'jobs': 'jobs',
            'listeners': 'listeners',
            'models': 'models',
            'services': 'services',
            'support': 'support',
        })

        # Merge defaults with package paths
        paths = defaults.merge(self.config.paths)

        if key in paths:
            return os.path.realpath(self.path + '/' + paths[key])
        return None

        # Convert all to realpaths
        # for key, value in paths.items():
        #     paths[key] = os.path.realpath(self.path + '/' + value)




# # OBSOLETE
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



# IoC Class Instance
# No because not to be used by the public
#Package: _Package = uvicore.ioc.make('Package', _Package, aliases=['package'])

# Public API for import * and doc gens
#__all__ = ['_Package']
