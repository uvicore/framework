config = {
    'version': '1.0.1',

    'test': 'original in foundation',

    'database': {
        'default': 'foundation',
        'connections': {
            'foundation': {
                'driver': 'mysql',
                'dialect': 'pymysql',
                'host': '127.0.0.1',
                'port': 3306,
                'database': 'foundation',
                'username': 'root',
                'password': 'techie',
                'prefix': None,
                'array': [
                    'orig1',
                    'orig2',
                ]
            },
        },
    },

    'register_web_routes': False,
    'register_api_routes': False,
    'register_views': False,
    'register_commands': True,

}
