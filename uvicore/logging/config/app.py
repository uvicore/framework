
# App and providers DO run if APP or LIBRARY mode
# Because even if module, it is a dependency graph
# So provider IMPORTER needs to not import things twice

# Providers should be a recursive dependency graph

config = {
    # Package Info
    'name': 'logging',
    'vendor': 'uvicore',
    'package': 'uvicore.logging',
    'config_prefix': 'uvicore.logging',

    # Application Service Providers
    'providers': [],
}
