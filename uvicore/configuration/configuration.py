import uvicore
from uvicore.support.dumper import dd, dump
from uvicore.contracts import Config as ConfigInterface


@uvicore.service('uvicore.configuration.configuration.Configuration',
    aliases=['Configuration', 'Config', 'configuration', 'config'],
    singleton=True,
)
class Configuration(ConfigInterface):
    pass



# IoC Class Instance
# Not to be imported by the public from here.
# Use the uvicore.config singleton global instead.

# Public API for import * and doc gens
#__all__ = ['_Configuration']
