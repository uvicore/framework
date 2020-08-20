import uvicore
from uvicore.package import ServiceProvider
from uvicore.support.dumper import dump, dd


class Logging(ServiceProvider):

    def register(self) -> None:
        """Register package into uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs and IoC bindings.  Configs are deep merged only after
        all packages are registered.  No real work should be performed here as it
        is very early in the bootstraping process and most internal processes are not
        instantiated yet.
        """
        # Note about logger config
        # We cannot use the standard package config/logger.py here with proper
        # app config overrides because the logger is SUPER early in the bootstrapping
        # process.  I want the log available almost first thing, even in your packages
        # service provider register() and boot() methods.  This means if the logger config
        # were in this packages config/logger.py file you wouldn't be able to override it
        # as usual from your own app.  So instead, the logger config is in your actual app config

        # Register IoC bindings
        override = self.binding('Logger')
        self.bind(
            name='Logger',
            object=override or 'uvicore.logging.logger._Logger',
            kwargs={'config': self.app_config.get('logger')},
            singleton=True,
            aliases=['Log', 'log', 'logger']
        )

        # Set uvicore.log global
        uvicore.log = uvicore.ioc.make('Logger')

    def boot(self) -> None:
        """Bootstrap package into uvicore framework.
        Boot takes place after all packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all configs.
        This is where you load views, assets, routes, commands...
        """
        pass
