import uvicore
from dataclasses import dataclass

# Pull original from Ioc
Base = uvicore.ioc.make('uvicore.package.Package_BASE')

@dataclass
class Package(Base):
    custom1: str
