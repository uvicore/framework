from uvicore.typing import Any, AsyncGenerator, Dict, List, Mapping, Optional, Union

import sqlalchemy as sa
#from databases import Database as EncodeDatabase
from sqlalchemy.sql import ClauseElement
from sqlalchemy.ext.asyncio import create_async_engine

import uvicore
from uvicore.contracts import Connection
from uvicore.contracts import Package as Package
from uvicore.contracts import Database as DatabaseInterface
from uvicore.database.query import DbQueryBuilder
from uvicore.support.dumper import dd, dump
from sqlalchemy.engine.result import Row as RowProxy


@uvicore.service('uvicore.database.db.Db',
    aliases=['Database', 'database', 'db'],
    singleton=True,
)
class Db(DatabaseInterface):
    """Database private class.

    Do not import from this location.
    Use the uvicore.db singleton global instead."""

    # Backends like sqlalchemy
    SUPPORTED_BACKENDS = [
        'sqlalchemy'
    ]

    # Dialects like postgresql (or postgres), mysql, sqlite
    SUPPORTED_DIALECTS = [
        'postgresql',
        'postgres',
        'mysql',
        'sqlite',
    ]

    # Async drivers like
    # Drivers are like pymysql, aiomysql, asyncio, psycopg2...
    # This is limited to encode supported drivers
    SUPPORTED_SYNC_DRIVERS = [
        # MySQL
        'mysqldb',
        'pymysql',
        'mysqlconnector',
        'mariadbconnector',
        # Postgres
        'psycopg2',
        'pg8000',
        # SQLite
        'pysqlite',
        # Oracle
        'cx_oracle',
        # MSSQL
        'pyodbc',
        'pymssql',
    ]

    SUPPORTED_ASYNC_DRIVERS = [
        # MySQL
        'aiomysql',
        'asyncmy',
        # Postgres
        'asyncpg',
        'aiopg',
        # SQLite
        'aiosqlite'
    ]

    @property
    def default(self) -> str:
        return self._default

    @property
    def connections(self) -> Dict[str, Connection]:
        return self._connections

    @property
    def engines(self) -> Dict[str, sa.engine.Engine]:
        return self._engines

    @property
    # def databases(self) -> Dict[str, EncodeDatabase]:
    def databases(self):
        return self._databases

    @property
    def metadatas(self) -> Dict[str, sa.MetaData]:
        return self._metadatas

    def __init__(self) -> None:
        self._default = None
        self._connections = Dict()
        self._engines = Dict()
        self._databases = Dict()
        self._metadatas = Dict()

    def init(self, default: str, connections: Dict[str, Connection]) -> None:
        """Tweak all connections and fill in URLs and Metadata. Runs from the app booted event."""

        # Loop all connections from all packages
        for connection_name, connection in connections.items():

            # Define some defaults regardless of backend type
            connection.defaults({
                'name': connection_name,
                'backend': 'sqlalchemy'
            })

            # Validate supported backends
            if connection.backend not in self.SUPPORTED_BACKENDS:
                raise Exception(f"A packages config/database.py connection backend {connection.backend} not supported by Uvicore.  Must be one of [{','.join(self.SUPPORTED_BACKENDS)}].")

            # Build url and metakey from connection configuration
            if connection.backend == 'sqlalchemy':

                # Define some defaults for SQLAlchemy backend specifically
                # Options is a superdict, which if a field doesn't exist produces a
                # blank Dict({}) not an empty string.  So merge with all possible defaults
                # for an sqlalchemy connection config
                connection.defaults({
                    'dialect': 'mysql',
                    'driver': 'aiomysql',
                    'host': '127.0.0.1',
                    'port': 3306,
                    'database': 'mysql',
                    'username': '',
                    'password': '',
                    'prefix': None
                })

                # All Optional must be strings, so convert all values to str()
                if connection.options:
                    for (key, value) in connection.options.items():
                        connection.options[key] = str(value)

                # Build an SQLAlchemy compatible URL from connection configuration dictionary
                # dialect+driver://<user>:<password>@<host>[:<port>]/<dbname>
                connection.url = (sa.engine.url.URL.create(
                    drivername=connection.dialect + '+' + connection.driver,
                    username=connection.username,
                    password=connection.password,
                    host=connection.host,
                    port=int(connection.port),
                    database=connection.database,
                    query=connection.options
                ))

                # Build metakey
                # Metakey is slightly different than the URL because we are trying to deduce
                # a single SERVER/HOST, not including the separate database itself
                connection.metakey = (
                    connection.dialect +
                    '@' + connection.host +
                    ':' + str(connection.port) +
                    '/' + connection.database
                )

                # Attempt an async connection, else a sync connection
                # And automatically set an is_async attribute on our connection Dict
                try:
                    engine = create_async_engine(connection.url)
                    connection.is_async = True
                except:
                    engine = sa.create_engine(connection.url, pool_pre_ping=True)
                    connection.is_async = False

                # Add this new [sync or async] engine to our Dict of engines
                self._engines[connection.metakey] = engine

                # Add this new metadata to our Dict of metadatas
                self._metadatas[connection.metakey] = sa.MetaData()

                #self._engines[connection.metakey] = sa.create_engine(connection.url)
                #self._databases[connection.metakey] = EncodeDatabase(encode_url, **connection.options)
                #self._metadatas[connection.metakey] = sa.MetaData()

        # Set instance variables
        self._default = default
        self._connections = connections

    def packages(self, connection: str = None, metakey: str = None) -> List[Package]:
        if not metakey:
            if not connection: connection = self.default
            metakey = self.connection(connection).metakey
        packages = []
        for package in uvicore.app.packages.values():
            if not 'database' in package: continue
            for conn in package.database.connections.values():
                if conn.metakey == metakey:
                    packages.append(package)
        return packages

    def metakey(self, connection: str = None, metakey: str = None) -> str:
        try:
            if not metakey:
                if not connection:
                    connection = self.default
                metakey = self.connection(connection).metakey
            return metakey
        except Exception:
            dump("ERROR Connections:", self.connections)
            raise Exception('Metakey not found, connection={} metakey={}'.format(connection, metakey))

    def connection(self, connection: str = None) -> Connection:
        if not connection: connection = self.default
        return self.connections.get(connection)

    def metadata(self, connection: str = None, metakey: str = None) -> sa.MetaData:
        metakey = self.metakey(connection, metakey)
        return self.metadatas.get(metakey)

    def tables(self, connection: str = None, metakey: str = None) -> List[sa.Table]:
        metadata = self.metadata(connection, metakey)
        return metadata.tables

    def table(self, table: str, connection: str = None) -> sa.Table:
        tablename = self.tablename(table, connection)
        metadata = self.metadata(connection)
        if metadata: return metadata.tables.get(tablename)

    def tablename(self, table: str, connection: str = None) -> str:
        if '.' in table:
            connection, table = tuple(table.split('.'))
        connection = self.connection(connection)
        if connection:
            if connection.prefix: return connection.prefix + table
            return table

    def engine(self, connection: str = None, metakey: str = None) -> sa.engine.Engine:
        metakey = self.metakey(connection, metakey)
        return self.engines.get(metakey)

    #async def database(self, connection: str = None, metakey: str = None) -> EncodeDatabase:
    async def database(self, connection: str = None, metakey: str = None):
        metakey = self.metakey(connection, metakey)

        # To connect on-the-fly or NOT on-the-fly, in the service uvicore_startup event, or both???

        # On-The-Fly ON Only
        # - When running from ./serve-uvicorn and using wrk -c10 -t4 -d5 http://0.0.0.0:5000/api/tags/1
        #   Notice the 2 IDs 0x7f733acc9130 and 0x7f733acc96d0 are different
        #     [ERROR] Exception in ASGI application
        #     File "/home/mreschke/.cache/pypoetry/virtualenvs/mreschke-speedtest-epfwGmSK-py3.9/lib/python3.9/site-packages/databases/backends/mysql.py", line 100, in release
        #       await self._database._pool.release(self._connection)
        #     File "/home/mreschke/.cache/pypoetry/virtualenvs/mreschke-speedtest-epfwGmSK-py3.9/lib/python3.9/site-packages/aiomysql/pool.py", line 204, in release
        #       assert conn in self._used, (conn, self._used)
        #     AssertionError: (<aiomysql.connection.Connection object at 0x7f733acc9130>, {<aiomysql.connection.Connection object at 0x7f733acc96d0>})

        # On-The-Fly OFF (using Service events Only)
        # - If off, during TESTING, uvicore.console.events.command.Startup event does not fire, so DB
        #   is not connected and all tests against DB fail (can't seed tables, canot query tables..)

        # Solution
        # Alter test suite to fire a uvicore.console.events.command.PytestStartup and add that event to db/services.py uvicore_startup handler

        # Connect on-the-fly - NO, NOT required anymore
        # self.connect(connection, metakey)

        # Return Encode database
        return self.databases.get(metakey)

    async def connect(self, connection: str = None, metakey: str = None, *, all_dbs: bool = False) -> None:
        if all_dbs:
            # Connect all DBs
            for metakey, database in uvicore.db.databases.items():
                if not database.is_connected:
                    try:
                        await database.connect()
                    except:
                        # Will catch if DB is not running or port/constr is wrong
                        pass
        else:
            # Connect a single DB
            metakey = self.metakey(connection, metakey)
            database = self.databases.get(metakey)  # Dont call self.database() as its recursive
            if not database.is_connected:
                try:
                    await database.connect()
                except:
                    # Will catch if DB is not running or port/constr is wrong
                    pass

    async def disconnect(self, connection: str = None, metakey: str = None, all_dbs: bool = False) -> None:
        if all_dbs:
            # Disconnect from all connected databases
            for database in self.databases.values():
                # Only disconnect if connected or will throw an error
                if database.is_connected:
                    await database.disconnect()
        else:
            # Disconnect from one database by connection str or metakey
            metakey = self.metakey(connection, metakey)
            database = self.databases.get(metakey)
            if database.is_connected:
                await database.disconnect()

    async def fetchall(self, query: Union[ClauseElement, str], values: Dict = None, connection: str = None, metakey: str = None) -> List[RowProxy]:
        # Get engine for this (or default) connection
        engine = self.engine(connection, metakey)

        # Convert connection string into actual connection Dict
        connection: Connection = self.connection(connection)

        if connection.is_async:
            # Fetchall with async driver
            async with engine.connect() as conn:
                cursor = await conn.execute(sa.text(query), values)
                return cursor.fetchall()
        else:
            with engine.connect() as conn:
                cursor = conn.execute(sa.text(query), values)
                return cursor.fetchall()

        # encode/databases
        # ----------------
        # database = await self.database(connection, metakey)
        # return await database.fetch_all(query, values)

    async def fetchone(self, query: Union[ClauseElement, str], values: Dict = None, connection: str = None, metakey: str = None) -> Optional[RowProxy]:
        # Get engine for this (or default) connection
        engine = self.engine(connection, metakey)

        # Convert connection string into actual connection Dict
        connection: Connection = self.connection(connection)

        if connection.is_async:
            # Fetchall with async driver
            async with engine.connect() as conn:
                cursor = await conn.execute(sa.text(query), values)
                return cursor.fetchone()
        else:
            with engine.connect() as conn:
                cursor = conn.execute(sa.text(query), values)
                return cursor.fetchone()


        # encode/databases
        # ----------------
        # database = await self.database(connection, metakey)
        # return await database.fetch_one(query, values)

    async def execute(self, query: Union[ClauseElement, str], values: Union[List, Dict] = None, connection: str = None, metakey: str = None) -> Any:
        # Get engine for this (or default) connection
        engine = self.engine(connection, metakey)

        # Convert connection string into actual connection Dict
        connection: Connection = self.connection(connection)

        if connection.is_async:
            # Execute with async driver
            async with engine.begin() as conn:
                return await conn.execute(query, values)
        else:
            with engine.begin() as conn:
                return conn.execute(query, values)

        # encode/databases
        # ----------------
        # database = await self.database(connection, metakey)
        # dd(database)
        # if type(values) == dict:
        #     return await database.execute(query, values)
        # elif type(values) == list:
        #     return await database.execute_many(query, values)
        # else:
        #     return await database.execute(query)

    #  async def iterate(self, query: Union[ClauseElement, str], values: dict = None, connection: str = None) -> AsyncGenerator[Mapping, None]:
    #     async with self.connection() as connection:
    #         async for record in connection.iterate(query, values):
    #             yield record

    def query(self, connection: str = None) -> DbQueryBuilder[DbQueryBuilder, Any]:
        if not connection: connection = self.default
        return DbQueryBuilder(connection)


# IoC Class Instance
# Not to be imported by the public from here.
# Use the uvicore.db singleton global instead.
