from uvicore.configuration import env
from uvicore.typing import OrderedDict


# --------------------------------------------------------------------------
# Database Connections
#
# Uvicore allows for multiple database connections (backends) each with
# their own connection name.  Use 'default' to set the default connection.
# Database doesn't just mean a local relational DB connection.  Uvicore
# ORM can also query remote APIs, CSVs, JSON files and smash them all
# together as if from a local database join!
# --------------------------------------------------------------------------
database = {
    'default': env('DATABASE_DEFAULT', 'app1'),
    'connections': {
        # SQLite Example
        'app1': {
            'backend': env('DB_APP1_BACKEND', 'sqlalchemy'),
            'dialect': env('DB_APP1_DIALECT', 'sqlite'),
            'driver': env('DB_APP1_DRIVER', 'aiosqlite'),
            'database': env('DB_APP1_DB', ':memory:'),
            'prefix': env('DB_APP1_PREFIX', None),
        },

        # MySQL Example
        # 'app1': {
        #     'backend': env('DB_APP1_BACKEND', 'sqlalchemy'),
        #     'dialect': env('DB_APP1_DIALECT', 'mysql'),
        #     'driver': env('DB_APP1_DRIVER', 'aiomysql'),
        #     'host': env('DB_APP1_HOST', '127.0.0.1'),
        #     'port': env.int('DB_APP1_PORT', 3306),
        #     'database': env('DB_APP1_DB', 'app1'),
        #     'username': env('DB_APP1_USER', 'root'),
        #     'password': env('DB_APP1_PASSWORD', 'techie'),
        #     'prefix': env('DB_APP1_PREFIX', None),
        # },

        # Example of ORM over Remote Uvicore API
        # NOT implemented yet
        # 'app1_remote': {
        #     'driver': 'api',
        #     'dialect': 'uvicore',
        #     'url': 'https://app1.example.com/api',
        #     'prefix': None
        # },
    },
}


# --------------------------------------------------------------------------
# Redis Connections
#
# Uvicore allows for multiple redis connections (backends) each with
# their own connection name.  Use 'default' to set the default connection.
# --------------------------------------------------------------------------
redis = {
    'default': env('REDIS_DEFAULT', 'app1'),
    'connections': {
        'app1': {
            'host': env('REDIS_APP1_HOST', '127.0.0.1'),
            'port': env.int('REDIS_APP1_PORT', 6379),
            'database': env.int('REDIS_APP1_DB', 0),
            'password': env('REDIS_APP1_PASSWORD', None),
        },
        'cache': {
            'host': env('REDIS_CACHE_HOST', '127.0.0.1'),
            'port': env.int('REDIS_CACHE_PORT', 6379),
            'database': env.int('REDIS_CACHE_DB', 2),
            'password': env('REDIS_CACHE_PASSWORD', None),
        },
    },
}
