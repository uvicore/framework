from collections import OrderedDict

config = {

    # --------------------------------------------------------------------------
    # Package Information
    # --------------------------------------------------------------------------
    'name': 'uvicore.foundation',


    # --------------------------------------------------------------------------
    # Service Providers Dependencies
    # --------------------------------------------------------------------------
    'services': OrderedDict({
        'uvicore.configuration': {
            'provider': 'uvicore.configuration.services.Configuration',
        },
        'uvicore.logging': {
            'provider': 'uvicore.logging.services.Logging',
        },
        'uvicore.database': {
            'provider': 'uvicore.database.services.Database',
        },
        'uvicore.orm': {
            'provider': 'uvicore.orm.services.Orm',
        },
        'uvicore.console': {
            'provider': 'uvicore.console.services.Console',
        },
        'uvicore.http': {
            'provider': 'uvicore.http.services.Http',
        },
        'uvicore.auth': {
            'provider': 'uvicore.auth.services.Auth',
        },
    }),

}
