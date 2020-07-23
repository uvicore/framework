
# App and providers DO run if APP or LIBRARY mode
# Because even if module, it is a dependency graph
# So provider IMPORTER needs to not import things twice

# Providers should be a recursive dependency graph

config = {
    # Package Info
    'name': 'foundation',
    'vendor': 'uvicore',
    'package': 'uvicore.foundation',
    'config_prefix': 'uvicore.foundation',

    'version': '1.0.1',

    # Application Service Providers
    'providers': [
        # mRcore Framework
        #'mrcore.support',
    ],

    'services': {
        'uvicore.logging': {
            'provider': 'uvicore.logging.services.Logging',
        },
    },
}
