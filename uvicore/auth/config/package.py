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
    # Web Configuration
    #
    # prefix: All web routes will be prefixed with this URI. Ex: '' or '/wiki'
    #         This is in addition to running apps web.prefix config
    # --------------------------------------------------------------------------
    'web': {
        'prefix': '/auth',
    },

    # --------------------------------------------------------------------------
    # Api Configuration
    #
    # prefix: All api routes will be prefixed with this URI. Ex: '' or '/wiki'
    #         This is in addition to running apps api.prefix config
    # --------------------------------------------------------------------------
    'api': {
        'prefix': '/auth',
    },


    # --------------------------------------------------------------------------
    # Database Connections
    # --------------------------------------------------------------------------
    'database': {
        'default': 'auth',
        'connections': {

            # SQLite Example
            'auth': {
                'backend': env('DB_AUTH_BACKEND', 'sqlalchemy'),
                'dialect': env('DB_AUTH_DIALECT', 'sqlite'),
                'driver': env('DB_AUTH_DRIVER', 'aiosqlite'),
                'database': env('DB_AUTH_DB', ':memory:'),
                'prefix': env('DB_AUTH_PREFIX', None),
            },

            # MySQL Example
            # 'auth': {
            #     'backend': env('DB_AUTH_BACKEND', 'sqlalchemy'),
            #     'dialect': env('DB_AUTH_DIALECT', 'mysql'),
            #     'driver': env('DB_AUTH_DRIVER', 'aiomysql'),

            #     #'sync_driver': env('DB_AUTH_SYNC_DRIVER', 'pymysql'),
            #     #'async_driver': env('DB_AUTH_ASYNC_DRIVER', 'aiomysql'),

            #     'host': env('DB_AUTH_HOST', '127.0.0.1'),
            #     'port': env.int('DB_AUTH_PORT', 3306),
            #     'database': env('DB_AUTH_DB', 'auth'),
            #     'username': env('DB_AUTH_USER', 'root'),
            #     'password': env('DB_AUTH_PASSWORD', 'techie'),
            #     'prefix': env('DB_AUTH_PREFIX', None),

            #     # All options are passed directly to the specific driver.
            #     #'options': {
            #     #    'ssl': env.bool('DB_AUTH_SSL', False),
            #     #}

            #     #'driver': 'sqlite',
            #     #'database': ':memory',
            #     #'database': '/tmp/x.db',
            #     #'prefix': None,
            # },
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
