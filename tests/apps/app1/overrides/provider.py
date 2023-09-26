import uvicore

# Pull original from Ioc
Base = uvicore.ioc.make('uvicore.package.provider.Provider_BASE')

class Provider(Base):
    custom1: str
