from uvicore.configuration import env
from .database import database, redis
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
