from uvicore.typing import OrderedDict

# This is the main app1 config.  All items here can be overridden
# when used inside other applications.  Accessible at config('acme.app1')

config = {

    # --------------------------------------------------------------------------
    # Web Configuration
    #
    # prefix: All web routes will be prefixed with this URI. Ex: '' or '/wiki'
    # --------------------------------------------------------------------------
    'web': {
        'prefix': '/wiki',
    },

    # --------------------------------------------------------------------------
    # Api Configuration
    #
    # prefix: All web routes will be prefixed with this URI. Ex: '' or '/wiki'
    # --------------------------------------------------------------------------
    'api': {
        'prefix': '/wiki',
    },


    # --------------------------------------------------------------------------
    # Database Connections
    # --------------------------------------------------------------------------
    'database': {
        'default': 'app1',
        'connections': {
            # SQLite
            # 'app1': {
            #     'driver': 'sqlite',
            #     #'dialect': 'pysqlite',
            #     'database': ':memory',
            # },

            # MySQL
            'app1': {
                'backend': 'sqlalchemy',
                'driver': 'mysql',
                'dialect': 'pymysql',
                'host': '127.0.0.1',
                'port': 3306,
                'database': 'uvicore_test',
                'username': 'root',
                'password': 'techie',
                'prefix': None,
            },

            'app1_remote': {
                'backend': 'api',
                'driver': 'uvicore.orm.drivers.api',
                'dialect': 'uvicore',
                'url': 'https://app1.example.com/api',
                'prefix': None,
            },
        },
    },


    # --------------------------------------------------------------------------
    # Redis Connections
    # --------------------------------------------------------------------------
    'redis': {
        'default': 'app1',
        'connections': {
            'app1': {
                'host': '127.0.0.1',
                'port': 6379,
                'database': 0,
                'password': None
            },
            'cache': {
                'host': '127.0.0.1',
                'port': 6379,
                'database': 9,
                'password': None
            },
        },
    },



    # --------------------------------------------------------------------------
    # Registration Control
    # --------------------------------------------------------------------------
    # This lets you control the service provider registrations.  If this app
    # is used as a package inside another app you might not want some things
    # registered in that context.  Use config overrides in your app to change
    # registrations
    # 'registers': {
    #     'web_routes': False,
    #     'api_routes': False,
    #     'middleware': False,
    #     'views': False,
    #     'assets': False,
    #     'commands': False,
    #     'models': False,
    #     'tables': False,
    #     'seeders': False,
    # },


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
    'dependencies': OrderedDict({
        'uvicore.foundation': {
            'provider': 'uvicore.foundation.services.Foundation',
        },
        'uvicore.database': {
            'provider': 'uvicore.database.services.Database',
        },
        'uvicore.orm': {
            'provider': 'uvicore.orm.services.Orm',
        },
        'uvicore.auth': {
            'provider': 'uvicore.auth.services.Auth',
        },
        'uvicore.http': {
            'provider': 'uvicore.http.services.Http',
        },
    }),

}
