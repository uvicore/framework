import uvicore
from uvicore.contracts import Application, Package
from uvicore.support.provider import ServiceProvider
from uvicore.support.dumper import dump, dd


class Configuration(ServiceProvider):

    def register(self) -> None:
        """Register package into uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs and IoC bindings.  Configs are deep merged only after
        all packages are registered.  No real work should be performed here as it
        is very early in the bootstraping process and most internal processes are not
        instantiated yet.
        """
        # Register IoC bindings
        override = self.binding('Configuration')
        self.bind(
            name='Configuration',
            object=override or 'uvicore.configuration.configuration._Configuration',
            singleton=True,
            aliases=['Config', 'config']
        )

        # Set uvicore.log global
        uvicore.config = uvicore.ioc.make('Config')

        # Set app.config for convenience (only after register since config is a service provider itself)
        self.app._config = uvicore.config

        # Set main app config
        uvicore.config.set('app', self.app_config)

    def boot(self) -> None:
        """Bootstrap package into uvicore framework.
        Boot takes place after all packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all configs.
        This is where you load views, assets, routes, commands...
        """
