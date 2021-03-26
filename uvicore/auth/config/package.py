from uvicore.configuration import env
from uvicore.typing import OrderedDict

# This is the main auth config.  All items here can be overridden
# when used inside other applications.  Accessible at config('uvicore.auth')

config = {

    # --------------------------------------------------------------------------
    # Argon2 Password Hasher Configuration
    # See https://argon2-cffi.readthedocs.io/en/stable/api.html
    # --------------------------------------------------------------------------
    'hasher': {
        'type': 'ID',
        'hash_len': 16,
        'salt_len': 16,
        'encoding': 'utf-8',
        'time_cost': 2,
        'memory_cost': 102400,
        'parallelism': 8,
    },


    # --------------------------------------------------------------------------
    # Route Configuration
    # --------------------------------------------------------------------------
    # Or like so, no underscores, so in dot notation config('blog.route.prefix')
    # have to do deep merges
    'route': {
        'web_prefix': '/auth',
        'api_prefix': '/auth/api',
    },


    # --------------------------------------------------------------------------
    # Database Connections
    # --------------------------------------------------------------------------
    'database': {
        'default': 'auth',
        'connections': {
            'auth': {
                'backend': env('AUTH_DB_BACKEND', 'sqlalchemy'),
                'driver': env('AUTH_DB_DRIVER', 'mysql'),
                'dialect': env('AUTH_DB_DIALECT', 'pymysql'),
                'host': env('AUTH_DB_HOST', '127.0.0.1'),
                'port': env.int('AUTH_DB_PORT', 3306),
                'database': env('AUTH_DB_DB', 'auth'),
                'username': env('AUTH_DB_USER', 'root'),
                'password': env('AUTH_DB_PASSWORD', 'techie'),
                'prefix': env('AUTH_DB_PREFIX', None),
            },
        },
    },


    # --------------------------------------------------------------------------
    # Registration Control
    # --------------------------------------------------------------------------
    # This lets you control the service provider registrations.  If this app
    # is used as a package inside another app you might not want some things
    # registered in that context.
    # 'registers': {
    #     'web_routes': True,
    #     'api_routes': True,
    #     'middleware': True,
    #     'views': True,
    #     'assets': True,
    #     'commands': True,
    #     'models': True,
    #     'tables': True,
    #     'seeders': True,
    # },


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
    # 'dependencies': OrderedDict({})

}
