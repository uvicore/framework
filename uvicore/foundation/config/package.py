from collections import OrderedDict

config = {

    # --------------------------------------------------------------------------
    # Package Information
    # --------------------------------------------------------------------------
    'name': 'uvicore.foundation',
    # 'name': 'foundation',
    # 'vendor': 'uvicore',
    # 'package': 'uvicore.foundation',
    'config_prefix': 'uvicore.foundation',


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
    }),

}
