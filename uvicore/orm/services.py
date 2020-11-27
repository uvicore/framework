import uvicore
from typing import Dict
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd

@uvicore.provider()
class Orm(ServiceProvider):

    def register(self) -> None:
        """Register package into uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs and IoC bindings.  Configs are deep merged only after
        all packages are registered.  No real work should be performed here as it
        is very early in the bootstraping process and most internal processes are not
        instantiated yet.
        """
        # Register IoC bindings
        # Automatic - self.bind('Model', 'uvicore.orm.model._Model', aliases=['model'])
        # Automatic - self.bind('ModelMetaclass', 'uvicore.orm.metaclass._ModelMetaclass')

        #self.bind('Model', 'uvicore.orm.model._Model', aliases=['model'])
        #self.bind('ModelMetaclass', 'uvicore.orm.metaclass._ModelMetaclass')

    def boot(self) -> None:
        """Bootstrap package into uvicore framework.
        Boot takes place after all packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all configs.
        This is where you load views, assets, routes, commands...
        """
        pass
