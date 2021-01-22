from .provider import ServiceProvider
#from uvicore.package.package import Package as _Package

# Proxy instead of import to create a nicer uvicore.package.Package namespace
# Even if you override this the acutal class, all listings will still show this consistent namespace
# NO - Not sure I like proxy as it creates 2 classes on 2 different paths which can cause issues in type()
# class Package(_Package):
#     pass


import uvicore
from uvicore.typing import Any
from uvicore.contracts import Connection
from uvicore.support.dumper import dump, dd
from prettyprinter import pretty_call, register_pretty
from uvicore.contracts import Package as PackageInterface


@uvicore.service(aliases=['Package', 'package'])
class Definition(PackageInterface):

    def config(self, dotkey: str = None) -> Any:
        """Helper to access this packages configs"""
        if dotkey:
            return uvicore.config(self.name + '.' + dotkey)
        else:
            return uvicore.config(self.name)

    def connection(self, name: str = None) -> Connection:
        """Helper to access this packages connections"""
        if not self.database.connections: return None
        if name:
            return next(connection for connection in self.database.connections if connection.name == name)
        else:
            return next(connection for connection in self.database.connections if connection.name == self.database.connection_default)
            #if 'database' in self.config():
            #    return next(connection for connection in self.connections if connection.name == self.config('database.default'))



@register_pretty(Definition)
def pretty_entity(value, ctx):
    """Custom pretty printer for my SuperDict"""
    # This printer removes the class name uvicore.types.Dict and makes it print
    # with a regular {.  This really cleans up the output!

    #return pretty_call(ctx, cls, **value.__dict__)
    #return pretty_call(ctx, 'Package', **value)
    return pretty_call(ctx, 'Package', value.to_dict())
