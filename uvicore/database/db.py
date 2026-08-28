import uvicore
import sqlalchemy as sa
from uvicore.contracts import Connection
from uvicore.support.dumper import dd, dump
from uvicore.contracts import Package as Package
from uvicore.database.query import DbQueryBuilder
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
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

    # A connection's optional 'pool' config block -> SQLAlchemy create_engine kwargs.
    #
    # WHY THIS IS CONFIG AND NOT HARDCODED.  Engine pooling is the one part of the database
    # layer whose right answer is entirely deployment-shaped: a days-long consumer wants
    # pre-ping and connection recycling, a request/response API wants a pool sized to its
    # worker count, and a warehouse with a per-warehouse concurrency ceiling wants that
    # ceiling respected.  The framework cannot guess any of it, so it must be settable.
    #
    # NAMES ARE DELIBERATELY UNPREFIXED here ('recycle', not 'pool_recycle'): the block is
    # already called 'pool', so repeating it would read as pool.pool_recycle.  SQLAlchemy's
    # own kwargs are inconsistent about the prefix ('pool_size' but 'max_overflow'), which
    # is exactly the kind of trivia a config file should not make anyone remember.
    POOL_OPTIONS = {
        'pre_ping':        'pool_pre_ping',
        'recycle':         'pool_recycle',
        'size':            'pool_size',
        'max_overflow':    'max_overflow',
        'timeout':         'pool_timeout',
        'use_lifo':        'pool_use_lifo',
        'reset_on_return': 'pool_reset_on_return',
    }

    # Applied when the connection sets no 'pool' block of its own.
    #
    # pre_ping defaults ON because the alternative is the worst failure mode a pool has: a
    # connection the server closed while it sat idle is handed to application code, which
    # then fails on a query it had no way to anticipate.  One cheap round-trip per checkout
    # buys that away.  Set 'pool': {'pre_ping': False} to opt out on a hot path.
    #
    # NOTHING ELSE IS DEFAULTED, on purpose.  pool_size/max_overflow are rejected outright
    # by SQLAlchemy's StaticPool and NullPool (which is what a sqlite ':memory:' url gets),
    # so a framework-level default would break the simplest connection there is.  Only keys
    # the app actually sets are ever passed through.
    POOL_DEFAULTS = {
        'pre_ping': True,
    }

    def __init__(self) -> None:
        self._default = None
        self._connections = Dict()
        self._engines = Dict()
        self._engine_urls = Dict()
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

                # If init() is called again (re-init) and an engine for this metakey already
                # exists with the SAME URL, reuse it.  Rebuilding an engine orphans its old
                # connection pool which can never be disposed, leaking driver connections that
                # finalize AFTER the event loop is closed (RuntimeError: Event loop is closed).
                existing_engine = self._engines.get(connection.metakey)
                if existing_engine is not None and self._engine_urls.get(connection.metakey) == connection.url:
                    continue

                # If the URL changed (ex: re-init with a new snowflake warehouse), dispose the
                # old engine BEFORE replacing it so its pooled connections are properly closed.
                if existing_engine is not None:
                    if isinstance(existing_engine, AsyncEngine):
                        # Cannot await in this sync method; schedule disposal on the running loop
                        import asyncio
                        try:
                            asyncio.get_running_loop().create_task(existing_engine.dispose())
                        except RuntimeError:
                            pass
                    else:
                        existing_engine.dispose()

                connect_args = dict(connection.options) if connection.options else {}

                # Pool kwargs come from the connection's 'pool' block (see POOL_OPTIONS).
                # Identical for sync and async engines - pre-ping used to be hardcoded true
                # on the sync branch and absent from the async one, which meant an async
                # app silently had no stale-connection protection at all.
                pool_kwargs = self.engine_pool_kwargs(connection)

                if connection.is_async:
                    engine = create_async_engine(connection.url, connect_args=connect_args, **pool_kwargs)
                else:
                    engine = sa.create_engine(connection.url, connect_args=connect_args, **pool_kwargs)

                # Dialect-specific resilience.  Snowflake needs SQLAlchemy taught that an
                # expired auth token is a DISCONNECT, or the dead connection is returned to
                # the pool and handed back out forever (see database/snowflake.py).  Armed
                # here, on engine creation, so an engine rebuilt by a re-init is re-armed.
                if connection.dialect == 'snowflake':
                    from uvicore.database.snowflake import register_dead_session_recovery
                    register_dead_session_recovery(engine)

                # Add this new [sync or async] engine + metadata keyed by metakey (preserve
                # existing metadata on re-init or ORM tables already registered would be lost)
                self._engines[connection.metakey] = engine
                self._engine_urls[connection.metakey] = connection.url
                if connection.metakey not in self._metadatas:
                    self._metadatas[connection.metakey] = sa.MetaData()

        # Set instance variables
        self._default = default
        self._connections = connections

    def engine_pool_kwargs(self, connection: Connection) -> Dict:
        """Translate a connection's 'pool' config block into create_engine kwargs.

        Pure (no engine creation, no live database) so every dialect's pooling can be
        unit-tested.  Unknown keys RAISE rather than being ignored: a silently-dropped
        'pool_recycle' (the prefixed spelling) would look configured and do nothing, and
        the whole point of the block is the failures it prevents."""

        pool = Dict(connection.pool) if connection.get('pool') else Dict()

        unknown = [key for key in pool.keys() if key not in self.POOL_OPTIONS]
        if unknown:
            raise Exception(
                "A packages config/database.py connection '{}' has unknown pool option(s) "
                '[{}].  Must be one of [{}].  Note these are UNPREFIXED (use \'recycle\', '
                "not \'pool_recycle\').".format(
                    connection.get('name'), ','.join(sorted(unknown)), ','.join(self.POOL_OPTIONS)
                )
            )

        pool.defaults(self.POOL_DEFAULTS)

        # None means "not set" so a config file can spell out every key it cares about and
        # leave the rest explicitly blank without accidentally passing None to SQLAlchemy.
        return Dict({
            self.POOL_OPTIONS[key]: value
            for key, value in pool.items()
            if value is not None
        })

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
                'options': {},
            })

            # KEEP THE SNOWFLAKE SESSION ALIVE BY DEFAULT.
            #
            # A Snowflake session holds a session token (~1h, which the connector renews)
            # and a MASTER token (~4h, which it does NOT - on 390114 it merely sets an
            # `expired` flag that nothing ever reads, and key-pair auth has no re-auth
            # path).  So without a heartbeat, EVERY process that outlives the master token
            # starts failing every query with '390114: Authentication token has expired',
            # permanently, until it is restarted.  A framework whose database connection
            # expires after four hours is not a working database connection, so this is a
            # default rather than something each app has to discover the hard way.
            #
            # `client_session_keep_alive` starts a per-connection heartbeat thread that
            # POSTs /session/heartbeat, refreshing the master token before it can expire.
            #
            # 900s, not the connector's 3600s default: the connector clamps the value to
            # [master_validity/16, master_validity/4] = [900, 3600] for the usual 4h
            # validity, and a heartbeat is a token-only REST call - it runs no query and
            # consumes NO warehouse credits - so the cheap end costs nothing and gives four
            # renewal chances per master-token window instead of one.
            #
            # .defaults() only fills what is MISSING, so an app that sets either key (or
            # sets keep-alive False for a short-lived CLI) always wins.
            connection.options.defaults({
                'client_session_keep_alive': True,
                'client_session_keep_alive_heartbeat_frequency': 900,
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

    async def disconnect(self, connection: str = None, metakey: str = None, all_dbs: bool = False) -> None:
        """Dispose one engine (by connection str or metakey) or all engines (all_dbs=True).
        Disposing an engine closes all pooled driver connections (aiomysql, asyncpg...).
        Async engines MUST be disposed before the event loop closes or their __del__
        finalizers fire on a dead loop (RuntimeError: Event loop is closed)."""
        if all_dbs:
            engines = list(self.engines.values())
        else:
            engine = self.engine(connection, metakey)
            engines = [engine] if engine is not None else []
        for engine in engines:
            if isinstance(engine, AsyncEngine):
                await engine.dispose()
            else:
                engine.dispose()

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
