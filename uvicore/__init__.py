from . import contracts
from .container import Ioc

# Uvicore version.  Also available in app.version
__version__ = '0.1.0'

# Core Global Variables
ioc: contracts.Ioc = Ioc()
events: contracts.Dispatcher = None
config: contracts.Config = None
app: contracts.Application = None
db: contracts.Database = None
log: contracts.Logger = None
