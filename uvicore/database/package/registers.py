from uvicore.typing import Dict, List
from uvicore.database import Connection
from uvicore.support.dumper import dump, dd
from uvicore.support.module import location


class Db:
    """Database Service Provider Mixin"""

    # def _add_db_definition(self, key, value):
        # if type(value) == list:
        #     if not self.package.database[key]: self.package.database[key] = []
        #     self.package.database[key].extend(value)
        # elif type(value) == dict:
        #     self.package.database[key].merge(value)
        # else:
        #     self.package.database[key] = value

        #self.package.database[key] = value

        # if 'database' not in self.package:
        #     self.package.database = Dict()
        # if type(value) == list:
        #     if key not in self.package.database: self.package.database = []
        #     self.package['database'][key].extend(value)
        # else:
        #     self.package['database'][key] = value

    def register_db_connections(self, connections: Dict, default: str):
        # for name, connection in connections.items():

        #     # Build URL and metakey
        #     # Metakey cannot be the connection name.  If 2 connections share the exact
        #     # same database (host, port, dbname) then they need to also share the same
        #     # metedata for foreign keys to work properly.

        #     if not connection.backend: connection.backend = 'sqlalchemy'
        #     connection.backend = connection.backend.lower()
        #     connection.driver = connection.driver.lower()
        #     url = ''
        #     metakey = ''

        #     if connection.backend == 'sqlalchemy':
        #         if connection.dialect == 'sqlite':
        #             url = 'sqlite:///' + connection.database
        #             metakey = url
        #         elif connection.dialect in ['mysql', 'postgresql', 'postgres']:
        #             url = (connection.dialect
        #                 + '+' + connection.driver
        #                 + '://' + connection.username
        #                 + ':' + connection.password
        #                 + '@' + connection.host
        #                 + ':' + str(connection.port)
        #                 + '/' + connection.database
        #             )
        #             metakey = (
        #                 connection.dialect
        #                 + '@' + connection.host
        #                 + ':' + str(connection.port)
        #                 + '/' + connection.database
        #             )
        #         # elif connection.dialect == 'snowflake':

        #         # Snowflake wip
        #         #from cryptography.hazmat.backends import default_backend
        #         #from cryptography.hazmat.primitives import serialization

        #         #     # NOTICE: FIXME
        #         #     # Snowflake does not work with database/encode
        #         #     # It may however work fine with SQLAlechemy 2.0 once we convert over

        #         #     # Once you get it working, here is what the CONFIG might look like
        #         #     # 'driver': 'snowflake',
        #         #     # # For private key auth - user, account and private_key are required (password should be blank)
        #         #     # 'account': env('DB_SF_ACCOUNT', 'account'),
        #         #     # 'database': env('DB_SF_DATABASE', ''),
        #         #     # 'schema': env('DB_SF_SCHEMA', ''),
        #         #     # 'warehouse': env('DB_SF_WAREHOUSE', ''),
        #         #     # 'role': env('DB_SF_ROLE', ''),
        #         #     # #'numpy': True,
        #         #     # #'cache_column_metadata': True,
        #         #     # # Username based
        #         #     # 'username': env('DB_SF_USERNAME', ''),
        #         #     # 'password': env('DB_SF_PASSWORD', ''),
        #         #     # #'authenticator': env('DB_SF_AUTHENTICATOR', 'externalbrowser'),
        #         #     # #'autocommit': True,
        #         #     # #'timezone': env('TIMEZONE', 'America/Chicago'),
        #         #     # #'paramstyle': env('DB_SF_PARAM_STYLE', 'numeric'),
        #         #     # 'private_key': env('DB_SF_PRIVATE_KEY', 'xxx'),
        #         #     # 'prefix': env('DB_SF_PREFIX', None),

        #         #     # See https://docs.snowflake.com/en/developer-guide/python-connector/sqlalchemy
        #         #     sep = '?'
        #         #     url += (
        #         #         'snowflake'
        #         #         + '://' + connection.username
        #         #         + ':' + connection.password
        #         #         + '@' + connection.account
        #         #     )

        #         #     # Optionally specify /database/schema
        #         #     if connection.database: url += '/' + connection.database
        #         #     if connection.schema: url += '/' + connection.schema

        #         #     # Using private key authentication
        #         #     # Required: username, account, private_key
        #         #     if connection.private_key:
        #         #         p_key = serialization.load_pem_private_key(
        #         #             (connection.private_key).encode('ascii'),
        #         #             password=None,
        #         #             backend=default_backend()
        #         #         )
        #         #         pkb = p_key.private_bytes(
        #         #             encoding=serialization.Encoding.DER,
        #         #             format=serialization.PrivateFormat.PKCS8,
        #         #             encryption_algorithm=serialization.NoEncryption()
        #         #         )
        #         #         url += "?connect_args={'private_key': " + str(pkb) + "}"
        #         #         sep = '&'

        #         #     if connection.warehouse:
        #         #         url += sep + 'warehouse=' + connection.warehouse
        #         #         sep = '&'
        #         #     if connection.role:
        #         #         url += sep + 'role=' + connection.role
        #         #         sep = '&'
        #         #     if connection.numpy:
        #         #         url += sep + 'numpy=' + str(connection.numpy)
        #         #         sep = '&'
        #         #     if connection.cache_column_metadata:
        #         #         url += sep + 'cache_column_metadata=' + str(connection.cache_column_metadata)
        #         #         sep = '&'

        #         #     metakey = (
        #         #         'snowflake'
        #         #         + '@' + connection.account
        #         #     )

        #     else:
        #         raise Exception(f"Connection backend {connection.backend} not supported")


        #     # Merge new values into connection SuperDict
        #     if not connection.prefix: connection.prefix = ''
        #     connection.merge({
        #         'name': name,
        #         'metakey': metakey.lower(),
        #         'url': url
        #     })
        #     #dd(connection, 'xx')

        self.package.database.connections = connections
        self.package.database.connection_default = default

    def register_db_models(self, items: List):
        # Default registration
        self.package.registers.defaults({'models': True})

        # Register models only if allowed
        if self.package.registers.models:
            self.package.database.models = items

    def register_db_tables(self, items: List):
        # Default registration
        self.package.registers.defaults({'tables': True})

        # Register tables only if allowed
        if self.package.registers.tables:
            self.package.database.tables = items

    def register_db_seeders(self, items: List):
        # Default registration
        self.package.registers.defaults({'seeders': True})

        # Register seeders only if allowed
        if self.package.registers.seeders:
            self.package.database.seeders = items
