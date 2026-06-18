"""
Dialect / connection-string robustness for the database layer.

Db.configure_connection() derives the SQLAlchemy URL, metakey and async flag for a
connection WITHOUT creating an engine or touching a live database, so we can validate
every supported dialect here (even ones whose driver package isn't installed).

Covers the cross-dialect contract the framework must get right so users aren't limited
to the few databases the author happened to test (SQLite, MySQL, Snowflake).
"""
import pytest


def configure(cfg):
    import uvicore
    from uvicore.contracts import Connection
    db = type(uvicore.db)()           # fresh Db instance (no global engine side effects)
    conn = Connection(cfg)
    db.configure_connection('c', conn)
    return conn


@pytest.mark.asyncio
async def test_postgres_alias_is_normalized(app1):
    """dialect 'postgres' must be normalized to 'postgresql' (SQLAlchemy dropped the alias)."""
    conn = configure({'dialect': 'postgres', 'host': 'h', 'database': 'd', 'username': 'u', 'password': 'p'})
    assert conn.dialect == 'postgresql'
    assert conn.url == 'postgresql+asyncpg://u:p@h:5432/d'
    assert conn.metakey == 'postgresql@h:5432/d'
    assert conn.is_async is True


@pytest.mark.asyncio
async def test_postgresql_explicit(app1):
    conn = configure({'dialect': 'postgresql', 'host': 'h', 'database': 'd', 'username': 'u', 'password': 'p'})
    assert conn.url == 'postgresql+asyncpg://u:p@h:5432/d'
    assert conn.is_async is True


@pytest.mark.asyncio
async def test_mysql_async_and_sync_drivers(app1):
    async_conn = configure({'dialect': 'mysql', 'host': 'h', 'database': 'd', 'username': 'u', 'password': 'p'})
    assert async_conn.url == 'mysql+aiomysql://u:p@h:3306/d'
    assert async_conn.is_async is True

    sync_conn = configure({'dialect': 'mysql', 'driver': 'pymysql', 'host': 'h', 'database': 'd', 'username': 'u', 'password': 'p'})
    assert sync_conn.url == 'mysql+pymysql://u:p@h:3306/d'
    assert sync_conn.is_async is False     # pymysql is a sync driver


@pytest.mark.asyncio
async def test_sqlite(app1):
    conn = configure({'dialect': 'sqlite', 'database': ':memory:'})
    assert conn.url == 'sqlite+aiosqlite:///:memory:'
    assert conn.metakey == 'sqlite://:memory:'
    assert conn.is_async is True


@pytest.mark.asyncio
async def test_additional_server_dialects(app1):
    """mariadb / mssql / oracle / cockroachdb build standard server URLs with sensible ports."""
    mariadb = configure({'dialect': 'mariadb', 'host': 'h', 'database': 'd', 'username': 'u', 'password': 'p'})
    assert mariadb.url == 'mariadb+aiomysql://u:p@h:3306/d' and mariadb.is_async is True

    mssql = configure({'dialect': 'mssql', 'host': 'h', 'database': 'd', 'username': 'u', 'password': 'p'})
    assert mssql.url == 'mssql+pyodbc://u:p@h:1433/d' and mssql.is_async is False

    oracle = configure({'dialect': 'oracle', 'host': 'h', 'database': 'd', 'username': 'u', 'password': 'p'})
    assert oracle.url == 'oracle+oracledb://u:p@h:1521/d' and oracle.is_async is True

    cockroach = configure({'dialect': 'cockroachdb', 'host': 'h', 'database': 'd', 'username': 'u', 'password': 'p'})
    assert cockroach.url == 'cockroachdb+asyncpg://u:p@h:26257/d' and cockroach.is_async is True


@pytest.mark.asyncio
async def test_psycopg3_async_driver_detected(app1):
    conn = configure({'dialect': 'postgresql', 'driver': 'psycopg', 'host': 'h', 'database': 'd', 'username': 'u', 'password': 'p'})
    assert conn.url == 'postgresql+psycopg://u:p@h:5432/d'
    assert conn.is_async is True


@pytest.mark.asyncio
async def test_explicit_url_is_respected(app1):
    """A user-provided url is used verbatim rather than being derived."""
    custom = 'postgresql+asyncpg://user:pw@example.com:6543/mydb'
    conn = configure({'dialect': 'postgresql', 'url': custom})
    assert conn.url == custom


@pytest.mark.asyncio
async def test_dialect_case_insensitive(app1):
    conn = configure({'dialect': 'PostgreSQL', 'host': 'h', 'database': 'd', 'username': 'u', 'password': 'p'})
    assert conn.dialect == 'postgresql'
    assert conn.url.startswith('postgresql+asyncpg://')


@pytest.mark.asyncio
async def test_unsupported_dialect_raises(app1):
    with pytest.raises(Exception, match='not supported'):
        configure({'dialect': 'nopedb'})


@pytest.mark.asyncio
async def test_unsupported_backend_raises(app1):
    with pytest.raises(Exception, match='not supported'):
        configure({'backend': 'magicdb', 'dialect': 'sqlite'})
