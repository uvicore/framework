config = {

    # --------------------------------------------------------------------------
    # Registration Control
    # --------------------------------------------------------------------------
    # This lets you control the service provider registrations.  If this app
    # is used as a package inside another app you might not want some things
    # registered in that context.
    'register_web_routes': True,
    'register_api_routes': True,
    'register_views': True,
    'register_assets': True,
    'register_commands': True,


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
                'driver': 'mysql',
                'dialect': 'pymysql',
                'host': '127.0.0.1',
                'port': 3306,
                'database': 'iam',
                'username': 'root',
                'password': 'techie',
                'prefix': None,
            },
        },
    },
}
