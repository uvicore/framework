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
        'uvicore.console': {
            'provider': 'uvicore.console.services.Console',
        },
        'uvicore.http': {
            'provider': 'uvicore.http.services.Http',
        },
    }),

}
