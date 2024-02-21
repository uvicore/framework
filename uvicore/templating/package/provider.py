import uvicore
from uvicore.package import Provider
from uvicore.support.dumper import dump, dd
from uvicore.templating.package import bootstrap
from uvicore.foundation.events import app as AppEvents


@uvicore.provider()
class Templating(Provider):

    def register(self) -> None:
        """Register package into the uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs, IoC bindings and early event listeners.
        Configs are deep merged only after all packages are registered.  No real
        work should be performed here as it is very early in the bootstraping
        process and we have no clear view of the full configuration system."""

        # Register event listeners
        # After all providers are booted we have a complete list of view paths
        # and template options fully merged.  Now we can fire up the static
        # paths and template system.
        AppEvents.Booted.listen(bootstrap.Templating)


    def boot(self) -> None:
        """Bootstrap package into the uvicore framework.
        Boot takes place after ALL packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all
        configuration. This is where you register, connections, models,
        views, assets, routes, commands...  If you need to perform work after ALL
        packages have booted, use the event system and listen to the booted event:
        self.events.listen('uvicore.foundation.events.app.Booted, self.booted')"""

        # Define Provider Registrations
        self.registers(self.package.config.registers)

