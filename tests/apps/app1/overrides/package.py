from __future__ import annotations
import uvicore

# Pull original from Ioc
Base = uvicore.ioc.make('uvicore.package.package.Package_BASE')

class Package(Base):
    custom1: str
