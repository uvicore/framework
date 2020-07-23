import uvicore
from uvicore.contracts import Package as PackageInterface


class _Package(PackageInterface):

    def config(self, dotkey: str = None):
        if dotkey:
            return uvicore.config(self.config_prefix + '.' + dotkey)
        else:
            return uvicore.config(self.config_prefix)

    def connection(self, name: str = None):
        if name:
            return next(connection for connection in self.connections if connection.name == name)
        else:
            return next(connection for connection in self.connections if connection.default == True)


# IoC Config class
Package: PackageInterface = uvicore.ioc.make('Package')

# Public API for import * and doc gens
__all__ = ['Package', '_Package']
