from .container import Ioc
from .contracts import Application as ApplicationInterface
from .contracts import Config as ConfigInterface
from .contracts import Logger as LoggerInterface
from .contracts import Dispatcher as DispatcherInterface

# Uvicore version.  Also available in app.version
__version__ = '0.1.0'

# Core Global Variables
ioc = Ioc()
events = DispatcherInterface = None
config: ConfigInterface = None
app: ApplicationInterface = None
log: LoggerInterface = None
