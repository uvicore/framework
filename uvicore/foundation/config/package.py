from collections import OrderedDict

config = {

    # --------------------------------------------------------------------------
    # Package Information
    # --------------------------------------------------------------------------
    'name': 'uvicore.foundation',


    # --------------------------------------------------------------------------
    # Package Dependencies (Service Providers)
    #
    # Careful to only define REQUIRED services.  Things like auth, db, http,
    # etc... are optional and specified in a packages dependencies if needed.
    # --------------------------------------------------------------------------
    'services': OrderedDict({
        # Configuration is used right away in provider register()
        'uvicore.configuration': {
            'provider': 'uvicore.configuration.services.Configuration',
        },

        # I want logging quick as it may be used in providers register() and boot()
        'uvicore.logging': {
            'provider': 'uvicore.logging.services.Logging',
        },

        'uvicore.console': {
            'provider': 'uvicore.console.services.Console',
        },

        # optional
        # 'uvicore.http': {
        #     'provider': 'uvicore.http.services.Http',
        # },

        # optional
        # 'uvicore.auth': {
        #     'provider': 'uvicore.auth.services.Auth',
        # },
    }),

}
