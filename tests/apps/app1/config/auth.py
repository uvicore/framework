config = {
    # --------------------------------------------------------------------------
    # Database Connections
    # --------------------------------------------------------------------------
    'database': {
        'default': 'auth',
        'connections': {
            # SQLite
            # 'auth': {
            #     'driver': 'sqlite',
            #     'dialect': None,
            #     'host': None,
            #     'port': None,
            #     'database': ':memory',
            #     'username': None,
            #     'password': None,
            #     'prefix': 'auth_',
            # },

            # MySQL
            'auth': {
                'driver': 'mysql',
                'dialect': 'pymysql',
                'host': '127.0.0.1',
                'port': 3306,
                'database': 'uvicore_test',
                'username': 'root',
                'password': 'techie',
                'prefix': 'auth_',
            },
        },
    },
}
