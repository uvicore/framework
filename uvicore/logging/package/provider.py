import uvicore
from uvicore.package import Provider
from uvicore.support.dumper import dump, dd


@uvicore.provider()
class Logging(Provider):

    def register(self) -> None:
        """Register package into the uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs, IoC bindings and early event listeners.
        Configs are deep merged only after all packages are registered.  No real
        work should be performed here as it is very early in the bootstraping
        process and we have no clear view of the full configuration system."""

        # Note about logger config
        # We cannot use the standard package config/logger.py here with proper
        # app config overrides because the logger is SUPER early in the bootstrapping
        # process.  I want the log available almost first thing, even in your packages
        # service provider register() and boot() methods.  This means if the logger config
        # were in this packages config/logger.py file you wouldn't be able to override it
        # as usual from your own app.  So instead, the logger config is in your actual app config

        # Register IoC bindings
        # self.bind('Logger', 'uvicore.logging.logger._Logger',
        #     aliases=['Log', 'log', 'logger'],
        #     kwargs={'config': self.app_config.get('logger')},
        #     singleton=True
        # )

        # Set uvicore.log global
        uvicore.log = uvicore.ioc.make('uvicore.logging.logger.Logger')

    def boot(self) -> None:
        """Bootstrap package into the uvicore framework.
        Boot takes place after ALL packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all
        configuration. This is where you register, connections, models,
        views, assets, routes, commands...  If you need to perform work after ALL
        packages have booted, use the event system and listen to the booted event:
        self.events.listen('uvicore.foundation.events.app.Booted', self.booted)"""

        # Define service provider registration control
        # No - Never allow this packages registrations to be disabled from other configs
        # ?? course I don't have any registrations for now, maybe later
