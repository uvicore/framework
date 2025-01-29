# type: ignore
from . import contracts
from uvicore.typing import Dict, TYPE_CHECKING
from uvicore.foundation.decorators import event, job, model, seeder, service, table, provider, routes, controller, composer


# Uvicore version.  Also available in app.version
__version__ = '0.3.0'

# Foundational
ioc: contracts.Ioc = None
events: contracts.Dispatcher = None
jobs: contracts.JobDispatcher = None
app: contracts.Application = None
config: contracts.Config = None
log: contracts.Logger = None
cache: contracts.Cache = None

# Optional
if TYPE_CHECKING:
    db: contracts.Database = None
else:
    db = None


def bootstrap(app_config: Dict, path: str, is_console: bool) -> None:
    """A pre-bootstrap method to setup and call the main uvicore application bootstrap"""

    # Order of imports is critical for proper IoC binding and override
    import uvicore
    from uvicore.support.dumper import dump, dd

    # Ensure app_config is a Uvicore Types Dict
    app_config = Dict(app_config)

    # Initialize the singleton IoC container
    # Before importing Application and Dispatcher which lets the IoC from app_config
    # swap even the earliest of core services
    from .container.ioc import Ioc
    uvicore.ioc = Ioc(app_config)

    # Import Application (which is an IoC singleton) and set uvicore.app global
    from uvicore.foundation.application import Application
    #uvicore.app = uvicore.ioc.make('uvicore.foundation.application.Application') # Also works
    uvicore.app = Application

    # Import Event Dispatcher (which is an IoC singleton) and set uvicore.events global
    # This cannot be a service provider because events are fired BEFORE any service providers
    # are ever loaded.
    from uvicore.events.dispatcher import Dispatcher
    uvicore.events = Dispatcher

    # Import Job Dispatcher
    from uvicore.jobs.dispatcher import Dispatcher as JobDispatcher
    uvicore.jobs = JobDispatcher

    # Why can 'config' be a service provider?  Because it's always the FIRST service provider.
    # So all other providers after that have access to register their own configs.

    # Bootstrap the actual uvicore Application
    uvicore.app.bootstrap(app_config, path, is_console)
