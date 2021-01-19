from collections import OrderedDict

# Package configuration is not meant to be overridden when used inside other
# apps.  This information is always unchanged and consistent.  The main
# wiki.py configuration however is meant to be overridden per use case.
# This is merged inside the main wiki.py and accessible at
# config('mreschke.wiki.package')

config = {

    # --------------------------------------------------------------------------
    # Package Information
    # --------------------------------------------------------------------------
    'name': 'uvicore.foundation',


    # --------------------------------------------------------------------------
    # Package Dependencies (Service Providers)
    #
    # Define all the packages that this package depends on.  At a minimum, only
    # the uvicore.foundation package is required.  The foundation is very
    # minimal and only depends on configuratino, logging and console itself.
    # You must add other core services built into uvicore only if your package
    # requires them.  Services like uvicore.database, uvicore.orm, uvicore.auth
    # uvicore.http, etc...
    # --------------------------------------------------------------------------
    'services': OrderedDict({
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
