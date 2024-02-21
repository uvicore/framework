from uvicore.typing import OrderedDict

# This is the main foundation config.  All items here can be overridden
# when used inside other applications.  Accessible at config('uvicore.foundation')

config = {

    # --------------------------------------------------------------------------
    # Registration Control
    #
    # This lets you control the service provider registrations.  If this app
    # is used as a package inside another app you might not want some things
    # registered in that context.  Use config overrides in your app to change
    # registrations
    # --------------------------------------------------------------------------
    'registers': {
        # 'web_routes': True,
        # 'api_routes': True,
        # 'middleware': True,
        # 'views': True,
        # 'assets': True,
        # 'commands': True,
        # 'models': True,
        # 'tables': True,
        # 'seeders': True,
    },


    # Just experimenting when commands being pulled from a config, probably
    # no need to do this
    # 'commands': {
    #     # Register Ioc commands
    #     'ioc': {
    #         'help': 'Uvicore Ioc (Inversion of Control) Information',
    #         'commands': {
    #             'bindings': 'uvicore.container.commands.ioc.bindings',
    #             'singletons': 'uvicore.container.commands.ioc.singletons',
    #             'overrides': 'uvicore.container.commands.ioc.overrides',
    #             'type': 'uvicore.container.commands.ioc.type',
    #             'get': 'uvicore.container.commands.ioc.get',
    #         },
    #     },

    #     # Register Package commands
    #     'package': {
    #         'help': 'Uvicore Package Information',
    #         'commands': {
    #             'providers': 'uvicore.package.commands.package.providers',
    #             'list': 'uvicore.package.commands.package.list',
    #             'get': 'uvicore.package.commands.package.get',
    #         },
    #     },

    #     # Register Event commands
    #     'event': {
    #         'help': 'Uvicore Event Information',
    #         'commands': {
    #             'list': 'uvicore.events.commands.event.list',
    #             'get': 'uvicore.events.commands.event.get',
    #             'listeners': 'uvicore.events.commands.event.listeners',
    #         },
    #     },
    # },


    # --------------------------------------------------------------------------
    # Package Dependencies (Package Providers)
    #
    # Define all the packages that this package depends on.  At a minimum, only
    # the uvicore.foundation package is required.  The foundation is very minimal
    # and only depends on configuration, logging and the console packages. You
    # must add other core services built into uvicore only if your package
    # requires them.  Services like uvicore.database, uvicore.orm, uvicore.auth
    # uvicore.http, etc...
    # --------------------------------------------------------------------------
    'dependencies': OrderedDict({
        # Careful to only define REQUIRED services for a minimal Uvicore.  Things
        # like auth, db, http, etc... are optional and specified in a packages
        # dependencies if needed.

        # Configuration is used right away in provider register()
        'uvicore.configuration': {
            'provider': 'uvicore.configuration.package.provider.Configuration',
        },

        # I want logging quick as it may be used in providers register() and boot()
        'uvicore.logging': {
            'provider': 'uvicore.logging.package.provider.Logging',
        },

        # Console is required for every uvicore app
        'uvicore.console': {
            'provider': 'uvicore.console.package.provider.Console',
        },

        # Cache is required for every uvicore app
        'uvicore.cache': {
            'provider': 'uvicore.cache.package.provider.Cache',
        },
    }),

}
