import uvicore

# Pull original from Ioc
Base = uvicore.ioc.make('uvicore.package.provider.ServiceProvider_BASE')

class ServiceProvider(Base):
    custom1: str
