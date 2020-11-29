import uvicore
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd

@uvicore.provider()
class Configuration(ServiceProvider):

    def register(self) -> None:
        """Register package into uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs and IoC bindings.  Configs are deep merged only after
        all packages are registered.  No real work should be performed here as it
        is very early in the bootstraping process and most internal processes are not
        instantiated yet."""

        # Register IoC bindings
        # self.bind('Configuration', 'uvicore.configuration.configuration._Configuration',
        #     aliases=['Config', 'config'],
        #     singleton=True,
        # )

        # Set uvicore.log global
        uvicore.config = uvicore.ioc.make('uvicore.configuration.configuration._Configuration')

        # Set app.config for convenience (only after register since config is a service provider itself)
        self.app._config = uvicore.config

        # Set main app config
        uvicore.config.set('app', self.app_config)

    def boot(self) -> None:
        """Bootstrap package into uvicore framework.
        Boot takes place after all packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all configs.
        This is where you load views, assets, routes, commands..."""

        pass
