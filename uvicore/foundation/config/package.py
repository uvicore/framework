from uvicore.support.collection import Odic

# Package configuration is not meant to be overridden when used inside other
# apps.  This information is always unchanged and consistent.  The main
# wiki.py configuration however is meant to be overridden per use case.
# This is merged inside the main wiki.py and accessible at
# config('mreschke.wiki.package')

config = {

    # --------------------------------------------------------------------------
    # Registration Control
    # --------------------------------------------------------------------------
    # This lets you control the service provider registrations.  If this app
    # is used as a package inside another app you might not want some things
    # registered in that context.
    'registers': {
        'web_routes': False,
        'api_routes': False,
        'middleware': False,
        'views': False,
        'assets': False,
        'commands': True,
        'models': False,
        'tables': False,
        'seeders': False,
    },


    # --------------------------------------------------------------------------
    # Package Dependencies (Service Providers)
    #
    # Define all the packages that this package depends on.  At a minimum, only
    # the uvicore.foundation package is required.  The foundation is very
    # minimal and only depends on configuratino, logging and console itself.
    # You must add other core services built into uvicore only if your package
    # requires them.  Services like uvicore.database, uvicore.orm, uvicore.http
    # uvicore.auth...
    # --------------------------------------------------------------------------
    'dependencies': Odic({
        # Careful to only define REQUIRED services for a minimal Uvicore.  Things
        # like auth, db, http, etc... are optional and specified in a packages
        # dependencies if needed.

        # Configuration is used right away in provider register()
        'uvicore.configuration': {
            'provider': 'uvicore.configuration.services.Configuration',
        },

        # I want logging quick as it may be used in providers register() and boot()
        'uvicore.logging': {
            'provider': 'uvicore.logging.services.Logging',
        },

        # Console is always required for every uvicore app
        'uvicore.console': {
            'provider': 'uvicore.console.services.Console',
        },
    }),

}
