from collections import OrderedDict

config = {

    # --------------------------------------------------------------------------
    # Package Information
    # --------------------------------------------------------------------------
    'name': 'uvicore.foundation',


    # --------------------------------------------------------------------------
    # Service Providers Dependencies
    # --------------------------------------------------------------------------
    # Careful to only define REQUIRED services.  Things like 'auth' are optional
    'services': OrderedDict({
        # Configuration is used right away in provider register()
        'uvicore.configuration': {
            'provider': 'uvicore.configuration.services.Configuration',
        },

        # I want logging quick as it may be used in providers register() and boot()
        'uvicore.logging': {
            'provider': 'uvicore.logging.services.Logging',
        },

        # optional
        # 'uvicore.database': {
        #     'provider': 'uvicore.database.services.Database',
        # },
        # 'uvicore.orm': {
        #     'provider': 'uvicore.orm.services.Orm',
        # },

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
