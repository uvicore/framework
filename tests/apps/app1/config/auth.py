config = {
    # --------------------------------------------------------------------------
    # Database Connections
    # --------------------------------------------------------------------------
    'database': {
        'default': 'auth',
        'connections': {
            'auth': {
                'driver': 'sqlite',
                'dialect': None,
                'host': None,
                'port': None,
                'database': ':memory',
                'username': None,
                'password': None,
                'prefix': 'auth_',
            },
        },
    },
}
