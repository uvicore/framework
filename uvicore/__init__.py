from .container import Ioc
from .contracts import Application as ApplicationInterface
from .contracts import Config as ConfigInterface
from .contracts import Logger as LoggerInterface
from .contracts import Dispatcher as DispatcherInterface
from .contracts import Database as DatabaseInterface
from .contracts import Ioc as IocInterface

# Uvicore version.  Also available in app.version
__version__ = '0.1.0'

# Core Global Variables
ioc: IocInterface = Ioc()
events: DispatcherInterface = None
config: ConfigInterface = None
app: ApplicationInterface = None
db: DatabaseInterface = None
log: LoggerInterface = None
