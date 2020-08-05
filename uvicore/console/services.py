import uvicore
from uvicore.support.provider import ServiceProvider
from uvicore.support.dumper import dump, dd


class Console(ServiceProvider):

    def register(self) -> None:
        """Register package into uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs and IoC bindings.  Configs are deep merged only after
        all packages are registered.  No real work should be performed here as it
        is very early in the bootstraping process and most internal processes are not
        instantiated yet.
        """
        # Register IoC bindings
        override = self.binding('Console')
        self.bind(
            name='Console',
            object=override or 'uvicore.console.console._cli',
            aliases=['console', 'cli']
        )

    def boot(self) -> None:
        """Bootstrap package into uvicore framework.
        Boot takes place after all packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all configs.
        This is where you load views, assets, routes, commands...
        """
        pass
