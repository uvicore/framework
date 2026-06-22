from uvicore.configuration import env


# --------------------------------------------------------------------------
# Env-driven connection builder
#
# Defaults to in-memory SQLite (the standard unit-test backend).  Set
# DB_<NAME>_DIALECT to a server dialect (postgresql, mysql, mariadb...) plus
# the matching host/port/user/password env vars to run the SAME schema and
# tests against a real database.  See tests/integration/ for the docker matrix.
# --------------------------------------------------------------------------
def connection(prefix: str, default_db: str = ':memory:'):
    dialect = env(f'{prefix}_DIALECT', 'sqlite')

    if dialect == 'sqlite':
        return {
            'backend': env(f'{prefix}_BACKEND', 'sqlalchemy'),
            'dialect': 'sqlite',
            'driver': env(f'{prefix}_DRIVER', 'aiosqlite'),
            'database': env(f'{prefix}_DB', ':memory:'),
            'prefix': env(f'{prefix}_PREFIX', None),
        }

    # Standard server-based dialect.  driver/port are omitted unless explicitly
    # provided so the framework's per-dialect defaults apply.
    conn = {
        'backend': env(f'{prefix}_BACKEND', 'sqlalchemy'),
        'dialect': dialect,
        'host': env(f'{prefix}_HOST', '127.0.0.1'),
        'database': env(f'{prefix}_DB', default_db),
        'username': env(f'{prefix}_USER', ''),
        'password': env(f'{prefix}_PASSWORD', ''),
        'prefix': env(f'{prefix}_PREFIX', None),
    }
    driver = env(f'{prefix}_DRIVER', None)
    if driver: conn['driver'] = driver
    port = env.int(f'{prefix}_PORT', None)
    if port: conn['port'] = port
    return conn


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
        'app1': connection('DB_APP1', default_db='app1'),

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
