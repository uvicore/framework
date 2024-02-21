from uvicore.configuration import env
from .database import database, redis
from uvicore.typing import OrderedDict
from .dependencies import dependencies


# --------------------------------------------------------------------------
# Package Configuration
#
# This is the packages configuration.  A package can RUN as an app or be
# used as a library inside another app.  The package config is always
# referenced regardless if the package is running as an APP or library.
# Accessible at config('testcli.version')
# --------------------------------------------------------------------------
config = {

    # --------------------------------------------------------------------------
    # Package Custom Configuration
    #
    # Your custom package specific configs go here
    # --------------------------------------------------------------------------
    # 'example': 'accessible at testcli.example',


    # --------------------------------------------------------------------------
    # Package Information
    #
    # Most other info like name, short_name, vendor are derived automatically
    # --------------------------------------------------------------------------
    'version': '0.1.0',


    # --------------------------------------------------------------------------
    # Web Configuration
    #
    # prefix: All web routes will be prefixed with this URI. Ex: '' or '/wiki'
    # --------------------------------------------------------------------------
    'web': {
        'prefix': '',
    },


    # --------------------------------------------------------------------------
    # Api Configuration
    #
    # prefix: All api routes will be prefixed with this URI. Ex: '' or '/wiki'
    # --------------------------------------------------------------------------
    'api': {
        'prefix': '',
    },


    # --------------------------------------------------------------------------
    # Registration Control
    #
    # This lets you control the service provider registrations.  If this app
    # is used as a package inside another app you might not want some things
    # registered in that context.  Use config overrides in your app to change
    # registrations
    # --------------------------------------------------------------------------
    'registers': {
        # 'web_routes': True,
        # 'api_routes': True,
        # 'middleware': True,
        # 'views': True,
        # 'templates': True,
        # 'assets': True,
        # 'commands': True,
        # 'models': True,
        # 'tables': True,
        # 'seeders': True,
    },


    # --------------------------------------------------------------------------
    # Path Overrides
    #
    # Override the default paths for your packages items (views, models,
    # tables, routes...).  All paths relative to your uvicore packages
    # PYTHON module root, not the actual package root. If item is not defined,
    # defaults will be assumed.  This is mainly used to "generate" schematics
    # like adding new controllers, commands and models from './uvicore gen' CLI
    # --------------------------------------------------------------------------
    'paths': {
        # 'commands': 'commands',
        # 'config': 'config',
        # 'database': 'database',
        # 'migrations': 'database/migrations',
        # 'seeders': 'database/seeders',
        # 'tables': 'database/tables',
        # 'events': 'events',
        # 'http': 'http',
        # 'api': 'http/api',
        # 'assets': 'http/assets',
        # 'controllers': 'http/controllers',
        # 'routes': 'http/routes',
        # 'static': 'http/static',
        # 'views': 'http/views',
        # 'view_composers': 'http/composers',
        # 'jobs': 'jobs',
        # 'listeners': 'listeners',
        # 'models': 'models',
    },


    # --------------------------------------------------------------------------
    # Include All Other Package Level Configs
    #
    # Split out into multiple files for a better user experience
    # --------------------------------------------------------------------------
    'database': database,
    'redis': redis,
    'dependencies': dependencies,
}








    # --------------------------------------------------------------------------
    # Database Connections
    # --------------------------------------------------------------------------
    # 'database': {
    #     'default': 'app1',
    #     'connections': {
    #         # SQLite
    #         # Leave this enabled for proper code coverage in db/provider.py connections()
    #         'app1_lite': {
    #             'driver': 'sqlite',
    #             #'dialect': 'pysqlite',
    #             'database': ':memory',
    #         },

    #         # MySQL
    #         'app1': {
    #             'backend': 'sqlalchemy',
    #             'driver': 'mysql',
    #             'dialect': 'pymysql',
    #             'host': '127.0.0.1',
    #             'port': 3306,
    #             'database': 'uvicore_test',
    #             'username': 'root',
    #             'password': 'techie',
    #             'prefix': None,
    #         },

    #         'app1_remote': {
    #             'backend': 'api',
    #             'driver': 'uvicore.orm.drivers.api',
    #             'dialect': 'uvicore',
    #             'url': 'https://app1.example.com/api',
    #             'prefix': None,
    #         },
    #     },
    # },


    # --------------------------------------------------------------------------
    # Redis Connections
    # --------------------------------------------------------------------------
    # 'redis': {
    #     'default': 'app1',
    #     'connections': {
    #         'app1': {
    #             'host': '127.0.0.1',
    #             'port': 6379,
    #             'database': 0,
    #             'password': None
    #         },
    #         'cache': {
    #             'host': '127.0.0.1',
    #             'port': 6379,
    #             'database': 9,
    #             'password': None
    #         },
    #     },
    # },



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
    # minimal and only depends on configuration, logging and console itself.
    # You must add other core services built into uvicore only if your package
    # requires them.  Services like uvicore.database, uvicore.orm, uvicore.auth
    # uvicore.http, etc...
    # --------------------------------------------------------------------------
    # 'dependencies': OrderedDict({
    #     'uvicore.foundation': {
    #         'provider': 'uvicore.foundation.package.provider.Foundation',
    #     },
    #     'uvicore.redis': {
    #         'provider': 'uvicore.redis.package.provider.Redis',
    #     },
    #     'uvicore.database': {
    #         'provider': 'uvicore.database.package.provider.Database',
    #     },
    #     'uvicore.orm': {
    #         'provider': 'uvicore.orm.package.provider.Orm',
    #     },
    #     'uvicore.auth': {
    #         'provider': 'uvicore.auth.package.provider.Auth',
    #     },
    #     'uvicore.http': {
    #         'provider': 'uvicore.http.package.provider.Http',
    #     },
    #     'uvicore.http_client': {
    #         'provider': 'uvicore.http_client.package.provider.HttpClient',
    #     },
    #     #'mreschke.themes': {
    #     #    'provider': 'mreschke.themes.package.provider.themes.Themes',
    #     #},
    # }),

#}
