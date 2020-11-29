from typing import Dict

from uvicore.foundation.decorators import model, seeder, service, table, provider

from . import contracts

# Uvicore version.  Also available in app.version
__version__ = '0.1.0'

# Core (non service provider based) singletons as globals
ioc: contracts.Ioc = None
events: contracts.Dispatcher = None
app: contracts.Application = None

# Core (service provider based) singletons as globals
config: contracts.Config = None
log: contracts.Logger = None
db: contracts.Database = None


def bootstrap(app_config: Dict, path: str, is_console: bool) -> None:
    """A pre-bootstrap method to setup and call the main uvicore application bootstrap"""

    # Order of imports is critical for proper IoC binding and override
    import uvicore

    # Initialize the singleton IoC container
    # Before importing Application and Dispatcher which lets the IoC from app_config
    # swap even the earliest of core services
    from .container.ioc import _Ioc
    uvicore.ioc = _Ioc(app_config)

    # Import Application (which is an IoC singleton) and set uvicore.app global
    from uvicore.foundation.application import _Application
    #uvicore.app = uvicore.ioc.make('uvicore.foundation.application.Application') # Also works
    uvicore.app = _Application

    # Import Event Dispatcher (which is an IoC singleton) and set uvicore.events global
    # This cannot be a service provider because events are fired BEFORE any service providers
    # are ever loaded.
    from uvicore.events.dispatcher import Dispatcher
    uvicore.events = Dispatcher

    # Why can 'config' be a service provider?  Because it's always the FIRST service provider.
    # So all other providers after that have access to register their own configs.

    # Bootstrap the actual uvicore Application
    uvicore.app.bootstrap(app_config, path, is_console)
