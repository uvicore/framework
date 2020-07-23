from .contracts import Application as ApplicationInterface
from .contracts import Config as ConfigInterface
from .contracts import Logger as LoggerInterface
from .container import Ioc
#from .foundation.package import Package as FoundationPackage
#from .support.dumper import dd, dump

__version__ = '0.1.0'


# Package class at base uvicore.Package
# Here so the namespace is nicer (simply uvicore.Package)
#class Package(FoundationPackage): pass

# Core Global Variables
ioc = Ioc()
config: ConfigInterface = None
app: ApplicationInterface = None
log: LoggerInterface = None
