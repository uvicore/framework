import uvicore
import sqlalchemy as sa
from uvicore.contracts import Connection
from uvicore.support.dumper import dd, dump
from uvicore.contracts import Package as Package
from uvicore.database.query import DbQueryBuilder
from sqlalchemy.ext.asyncio import create_async_engine
from uvicore.contracts import Database as DatabaseInterface
from typing import Any, List, Sequence, Mapping
from uvicore.typing import Dict


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

    # Dialects like postgresql (or postgres), mysql, sqlite.  Any standard SQLAlchemy
    # server dialect is supported as long as its driver package is installed; 'postgres'
    # is accepted as an alias and normalized to 'postgresql'.
    SUPPORTED_DIALECTS = [
        'postgresql',
        'postgres',
        'mysql',
        'mariadb',
        'sqlite',
        'snowflake',
        'mssql',
        'oracle',
        'cockroachdb',
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
        # MySQL / MariaDB
        'aiomysql',
        'asyncmy',
        # Postgres
        'asyncpg',
        'aiopg',
        'psycopg',      # psycopg3 has a native async mode
        # SQLite
        'aiosqlite',
        # MSSQL
        'aioodbc',
        # Oracle
        'oracledb',     # python-oracledb supports async
    ]

    @property
    def default(self) -> str:
        """The default connection str for the main running app"""
        return self._default

    @property
    def connections(self) -> Dict[str, Connection]:
        """All connections from all packages, keyed by connection str name"""
        return self._connections

    @property
    def engines(self) -> Dict[str, sa.engine.Engine]:
        """All engines for all unique (by metakey) connections, keyed by metakey"""
        return self._engines

    @property
    def metadatas(self) -> Dict[str, sa.MetaData]:
        """All SQLAlchemy Metadata for all unique (by metakey) connections, keyed by metakey"""
        return self._metadatas

    def __init__(self) -> None:
        self._default = None
        self._connections = Dict()
        self._engines = Dict()
        self._metadatas = Dict()

    # Per-dialect (default driver, default port) for standard server-based dialects.
    # Any SQLAlchemy server dialect works as long as its driver package is installed.
    SERVER_DIALECT_DEFAULTS = {
        'mysql':       ('aiomysql', 3306),
        'mariadb':     ('aiomysql', 3306),
        'postgresql':  ('asyncpg', 5432),
        'cockroachdb': ('asyncpg', 26257),
        'mssql':       ('pyodbc', 1433),
        'oracle':      ('oracledb', 1521),
    }

    def init(self, default: str, connections: Dict[str, Connection]) -> None:
        """Initialize the database system with a default connection str and List of all Connections from all packages"""

        # Loop all connections from all packages
        connection: Connection
        for connection_name, connection in connections.items():

            # Configure the connection (defaults, url, metakey, is_async).  Pure, no engine
            # creation, so it is independently unit-testable for every dialect.
            self.configure_connection(connection_name, connection)

            # Create the actual SQLAlchemy [async or sync] engine
            if connection.backend == 'sqlalchemy':
                connect_args = dict(connection.options) if connection.options else {}
                if connection.is_async:
                    engine = create_async_engine(connection.url, connect_args=connect_args)
                else:
                    engine = sa.create_engine(connection.url, connect_args=connect_args, pool_pre_ping=True)

                # Add this new [sync or async] engine + metadata keyed by metakey
                self._engines[connection.metakey] = engine
                self._metadatas[connection.metakey] = sa.MetaData()

        # Set instance variables
        self._default = default
        self._connections = connections

    def configure_connection(self, connection_name: str, connection: Connection) -> Connection:
        """Normalize, validate and derive url/metakey/is_async for one connection.

        Separated from engine creation so the connection-string and async logic can be
        validated for every dialect without a live database or installed driver.
        """
        # Define some defaults regardless of backend type
        connection.defaults({
            'name': connection_name,
            'backend': 'sqlalchemy',
            'dialect': 'sqlite',
        })

        # Standardize case
        connection.backend = connection.backend.lower()
        connection.dialect = connection.dialect.lower()

        # Normalize dialect aliases.  SQLAlchemy 1.4+ dropped the 'postgres' alias and
        # only accepts 'postgresql', so map it here (config may use either).
        if connection.dialect == 'postgres': connection.dialect = 'postgresql'

        # Validate supported backends
        if connection.backend not in self.SUPPORTED_BACKENDS:
            raise Exception(f"A packages config/database.py connection backend {connection.backend} not supported by Uvicore.  Must be one of [{','.join(self.SUPPORTED_BACKENDS)}].")

        # Validate supported dialects
        if connection.dialect not in self.SUPPORTED_DIALECTS:
            raise Exception(f"A packages config/database.py connection dialect {connection.dialect} not supported by Uvicore.  Must be one of [{','.join(self.SUPPORTED_DIALECTS)}].")

        if connection.backend != 'sqlalchemy':
            return connection

        if connection.dialect == 'sqlite':
            # SQLite has no host/port and a file (or :memory:) based URL
            connection.defaults({
                'driver': 'aiosqlite',
                'host': '',
                'port': '',
                'database': ':memory:',
                'prefix': None,
            })
            conn_url = connection.url or sa.engine.url.URL.create(
                drivername=f"{connection.dialect}+{connection.driver}",
                database=connection.database,
            )
            connection.metakey = connection.dialect + '://' + connection.database

        elif connection.dialect == 'snowflake':
            connection.defaults({
                'account': '', 'database': '', 'schema': '', 'warehouse': '',
                'username': '', 'role': '', 'password': '', 'private_key': '', 'prefix': None,
            })
            conn_url = connection.url or (
                f"{connection.dialect}://{connection.username}:{connection.password}"
                f"@{connection.account}/{connection.database}/{connection.schema}"
                f"?warehouse={connection.warehouse}&role={connection.role}"
            )
            connection.metakey = connection.dialect + '@' + connection.account + '/' + connection.role

        else:
            # Any standard server-based dialect (postgresql, mysql, mariadb, mssql, oracle,
            # cockroachdb...).  URL shape is identical: dialect+driver://user:pass@host:port/db
            (default_driver, default_port) = self.SERVER_DIALECT_DEFAULTS.get(connection.dialect, (None, None))
            connection.defaults({
                'driver': default_driver,
                'host': '127.0.0.1',
                'port': default_port,
                'database': '',
                'username': '',
                'password': '',
                'prefix': None,
            })
            conn_url = connection.url or sa.engine.url.URL.create(
                drivername=f"{connection.dialect}+{connection.driver}",
                username=connection.username,
                password=connection.password,
                host=connection.host,
                port=int(connection.port) if connection.port else None,
                database=connection.database,
            )
            # Metakey identifies a single SERVER/database (not the driver), so the same
            # server reached via different drivers shares one engine/metadata.
            connection.metakey = f"{connection.dialect}@{connection.host}:{connection.port}/{connection.database}"

        # Store url as a string WITH the real password (str(URL) masks it as ***, which
        # would make the stored url unusable for engine creation/reuse).  The password is
        # already present in plaintext on connection.password, so this exposes nothing new.
        if hasattr(conn_url, 'render_as_string'):
            connection.url = conn_url.render_as_string(hide_password=False)
        else:
            connection.url = str(conn_url)

        # Deterministic async vs sync based on the driver (no fragile bare-except that
        # could silently mask real connection errors as a sync fallback).
        connection.is_async = str(connection.driver) in self.SUPPORTED_ASYNC_DRIVERS

        return connection

    def packages(self, connection: str = None, metakey: str = None) -> List[Package]:
        """Get all packages with the metakey (direct or derived from connection str)."""

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
        """Get one metekay by connection str or metakey"""
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
        """Get one connection by connection name"""
        if not connection: connection = self.default
        return self.connections.get(connection)

    def metadata(self, connection: str = None, metakey: str = None) -> sa.MetaData:
        """Get one SQLAlchemy Metadata by connection str or metakey"""
        metakey = self.metakey(connection, metakey)
        return self.metadatas.get(metakey)

    def tables(self, connection: str = None, metakey: str = None) -> List[sa.Table]:
        """Get all SQLAlchemy tables for a given connection str or metakey"""
        metadata = self.metadata(connection, metakey)
        return metadata.tables

    def table(self, table: str, connection: str = None) -> sa.Table:
        """Get one SQLAlchemy Table by name (without prefix) and connection str or connection.tablename dot notation"""
        tablename = self.tablename(table, connection)
        metadata = self.metadata(connection)
        if metadata: return metadata.tables.get(tablename)

    def tablename(self, table: str, connection: str = None) -> str:
        """Get a SQLAlchemy tablename with prefix by name (without prefix) and connection str or connection.tablename dot notation"""
        if '.' in table:
            connection, table = tuple(table.split('.'))
        connection = self.connection(connection)
        if connection:
            if connection.prefix: return connection.prefix + table
            return table

    def engine(self, connection: str = None, metakey: str = None) -> sa.engine.Engine:
        """Get one SQLAlchemy Engine by connection str or metakey"""
        metakey = self.metakey(connection, metakey)
        return self.engines.get(metakey)

    def query(self, connection: str = None) -> DbQueryBuilder[DbQueryBuilder, Any]:
        """Database query builder passthrough"""
        if not connection: connection = self.default
        return DbQueryBuilder(connection)

    async def execute(
        self,
        query: Any,
        values: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
        connection: str | None = None,
        metakey: str | None = None
    ) -> sa.CursorResult:
        """Execute a SQLAlchemy Core Query based on connection str or metakey"""

        # Get engine for this (or default) connection
        engine = self.engine(connection, metakey)

        # Convert connection string into actual connection Dict
        connection: Connection = self.connection(connection)

        # If using raw SQL string
        if type(query) == str: query = sa.text(query)

        conn: sa.Connection
        if connection.is_async:
            # Execute with async driver
            async with engine.begin() as conn:
                # To dump raw SQL use str() - dd(str(query))
                # To get single inserted PK - result.inserted_primary_key
                # To get bulk inserted PK lists (not supported by MySQL) - result.inserted_primary_key_rows
                result: sa.CursorResult = await conn.execute(query, values)
                return result
        else:
            with engine.begin() as conn:
                result: sa.CursorResult = conn.execute(query, values)
                return result

    async def all(self,
        query: sa.Select|str,
        values: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
        connection: str | None = None,
        metakey: str | None = None
    ) -> Sequence[sa.Row]:
        """Get many records from query. Returns empty List if no records found"""
        result = await self.execute(query, values, connection, metakey)
        return result.all()

    async def fetchall(self,
        query: sa.Select|str,
        values: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
        connection: str | None = None,
        metakey: str | None = None
    ) -> Sequence[sa.Row]:
        """Alias to .all()"""
        return await self.all(query, values, connection, metakey)

    async def first(self,
        query: sa.Select|str,
        values: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
        connection: str | None = None,
        metakey: str | None = None
    ) -> sa.Row|None:
        """Get one (first/top) record from query. Returns None if no records found"""
        result = await self.execute(query, values, connection, metakey)
        return result.first()

    async def fetchone(self,
        query: sa.Select|str,
        values: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
        connection: str | None = None,
        metakey: str | None = None
    ) -> sa.Row|None:
        """Alias to .first()"""
        result = await self.execute(query, values, connection, metakey)
        return result.fetchone()

    async def one(self,
        query: sa.Select|str,
        values: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
        connection: str | None = None,
        metakey: str | None = None
    ) -> sa.Row:
        """Get one record from query. Throws Exception if no data found or querying more than one record"""
        result = await self.execute(query, values, connection, metakey)
        return result.one()

    async def one_or_none(self,
        query: sa.Select|str,
        values: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
        connection: str | None = None,
        metakey: str | None = None
    ) -> sa.Row|None:
        """Get one record from query.  Returns None if no record found.  Throws Exception of querying more than one record"""
        result = await self.execute(query, values, connection, metakey)
        return result.one_or_none()

    async def scalars(self,
        query: sa.Select|str,
        values: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
        connection: str | None = None,
        metakey: str | None = None
    ) -> Sequence[Any]:
        """Get many scalar values from query.  Returns empty List if no records found. If selecting multiple columns, returns List of FIRST column only."""
        result = await self.execute(query, values, connection, metakey)
        return result.scalars().all()

    async def scalar(self,
        query: sa.Select|str,
        values: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
        connection: str | None = None,
        metakey: str | None = None
    ) -> Any|None:
        """Get a single scalar value from query. Returns None if no record found.  Returns first (top) if more than one record found"""
        result = await self.execute(query, values, connection, metakey)
        return result.scalar()

    async def scalar_one(self,
        query: sa.Select|str,
        values: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
        connection: str | None = None,
        metakey: str | None = None
    ) -> Any:
        """Get a single scalar value from query.  Throws Exception if no data found or if querying more than one record"""
        result = await self.execute(query, values, connection, metakey)
        return result.scalar_one()

    async def scalar_one_or_none(self,
        query: sa.Select|str,
        values: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
        connection: str | None = None,
        metakey: str | None = None
    ) -> Any|None:
        """Get a single scalar value from query.  Returns None if no record found.  Throws Exception if querying more than one record"""
        result = await self.execute(query, values, connection, metakey)
        return result.scalar_one_or_none()

    async def insertmany(self,
        query: sa.Insert|str,
        values: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
        connection: str | None = None,
        metakey: str | None = None
    ) -> List[sa.Row]:
        """Bulk insert many rows, returning bulk primary keys (for databases that support INSERT..RETURNING)"""
        # For bulk returns see https://docs.sqlalchemy.org/en/20/core/connections.html#engine-insertmanyvalues
        result = await self.execute(query, values, connection, metakey)
        return result.inserted_primary_key_rows

    async def insertone(self,
        query: sa.Insert|str,
        values: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
        connection: str | None = None,
        metakey: str | None = None
    ) -> sa.Row:
        """Insert one row, returning the one rows PK (as a tuple in case of dual PKs)"""
        result = await self.execute(query, values, connection, metakey)
        return result.inserted_primary_key


# IoC Class Instance
# Not to be imported by the public from here.
# Use the uvicore.db singleton global instead.
