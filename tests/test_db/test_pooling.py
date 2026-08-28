"""
Engine POOL configuration and Snowflake session resilience.

Pooling used to be hardcoded: `pool_pre_ping=True` on the sync branch of `Db.init()` and
nothing at all on the async branch, with no way for an app to change either.  That is now
a per-connection 'pool' config block (`Db.engine_pool_kwargs`, pure so it is testable for
every dialect without a live database).

The Snowflake half guards a failure that is invisible for hours and then permanent: a
Snowflake MASTER token expires after ~4h and the connector does NOT renew it (it sets an
`expired` flag nothing reads), so every long-running process began failing every query
with `390114: Authentication token has expired` - and stayed broken until restarted,
because snowflake-sqlalchemy defines no `is_disconnect()` and SQLAlchemy therefore returned
the dead connection to the pool and handed it back out forever.
"""
import pytest


# uvicore.database cannot be imported at MODULE level: its @uvicore.service decorators need
# a booted IoC container, which the app1 fixture provides.  Every helper below imports
# lazily for that reason (the same pattern as test_dialects.py / test_engine_lifecycle.py).
def sf():
    from uvicore.database import snowflake
    return snowflake


def is_dead_session_error(exception):
    return sf().is_dead_session_error(exception)


def register_dead_session_recovery(engine):
    return sf().register_dead_session_recovery(engine)


def fresh_db():
    import uvicore
    return type(uvicore.db)()          # fresh Db instance (no global engine side effects)


def configure(cfg):
    from uvicore.contracts import Connection
    db = fresh_db()
    conn = Connection(cfg)
    db.configure_connection('c', conn)
    return db, conn


def pool_kwargs(cfg):
    db, conn = configure(cfg)
    return dict(db.engine_pool_kwargs(conn))


# --------------------------------------------------------------------------
# Db.engine_pool_kwargs - the 'pool' config block
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_pre_ping_is_on_by_default(app1):
    """The old hardcoded sync behavior is preserved as the default."""
    assert pool_kwargs({'dialect': 'sqlite', 'database': ':memory:'}) == {'pool_pre_ping': True}


@pytest.mark.asyncio
async def test_nothing_but_pre_ping_is_defaulted(app1):
    """pool_size/max_overflow are REJECTED by StaticPool/NullPool, which is what a sqlite
    ':memory:' url gets - so defaulting them would break the simplest connection there is."""
    kwargs = pool_kwargs({'dialect': 'sqlite', 'database': ':memory:'})
    assert 'pool_size' not in kwargs
    assert 'max_overflow' not in kwargs
    assert 'pool_recycle' not in kwargs


@pytest.mark.asyncio
async def test_pre_ping_can_be_turned_off(app1):
    """The whole point of the change: it is no longer hardcoded."""
    assert pool_kwargs({
        'dialect': 'sqlite', 'database': ':memory:', 'pool': {'pre_ping': False},
    }) == {'pool_pre_ping': False}


@pytest.mark.asyncio
async def test_every_pool_option_maps_to_its_sqlalchemy_kwarg(app1):
    """Names are unprefixed in config; SQLAlchemy's own are inconsistently prefixed
    ('pool_size' but 'max_overflow'), so the mapping is what has to be right."""
    assert pool_kwargs({
        'dialect': 'postgresql', 'host': 'h', 'database': 'd', 'username': 'u', 'password': 'p',
        'pool': {
            'pre_ping': True,
            'recycle': 1800,
            'size': 10,
            'max_overflow': 5,
            'timeout': 30,
            'use_lifo': True,
            'reset_on_return': 'rollback',
        },
    }) == {
        'pool_pre_ping': True,
        'pool_recycle': 1800,
        'pool_size': 10,
        'max_overflow': 5,
        'pool_timeout': 30,
        'pool_use_lifo': True,
        'pool_reset_on_return': 'rollback',
    }


@pytest.mark.asyncio
async def test_none_means_not_set(app1):
    """So a config file can spell out every key it cares about and leave the rest blank
    without passing None into SQLAlchemy."""
    kwargs = pool_kwargs({
        'dialect': 'sqlite', 'database': ':memory:',
        'pool': {'recycle': None, 'size': None, 'pre_ping': True},
    })
    assert kwargs == {'pool_pre_ping': True}


@pytest.mark.asyncio
async def test_unknown_pool_option_raises_and_names_the_valid_ones(app1):
    """A silently-ignored 'pool_recycle' (the PREFIXED spelling, the obvious mistake) would
    look configured and do nothing - the exact class of bug this block exists to prevent."""
    with pytest.raises(Exception) as e:
        pool_kwargs({
            'dialect': 'sqlite', 'database': ':memory:', 'pool': {'pool_recycle': 1800},
        })
    message = str(e.value)
    assert 'pool_recycle' in message
    assert 'recycle' in message          # the correct, unprefixed spelling is suggested


@pytest.mark.asyncio
async def test_pool_kwargs_reach_a_real_engine_sync_and_async(app1):
    """init() must apply the pool block identically on BOTH branches.  Async engines
    previously got NO pool arguments at all, so they silently had no pre-ping."""
    from uvicore.typing import Dict
    from uvicore.contracts import Connection

    # aiosqlite -> async engine.  pre_ping off so we can prove the value came from config
    # rather than from a default that happens to match.
    db = fresh_db()
    conns = Dict({'c': Connection({
        'dialect': 'sqlite', 'database': ':memory:', 'pool': {'pre_ping': False},
    })})
    db.init('c', conns)
    engine = db.engine('c')
    assert engine.sync_engine.pool._pre_ping is False

    # pysqlite -> sync engine, recycle set.
    db2 = fresh_db()
    conns2 = Dict({'c': Connection({
        'dialect': 'sqlite', 'driver': 'pysqlite', 'database': ':memory:',
        'pool': {'pre_ping': True, 'recycle': 1800},
    })})
    db2.init('c', conns2)
    engine2 = db2.engine('c')
    assert engine2.pool._pre_ping is True
    assert engine2.pool._recycle == 1800


# --------------------------------------------------------------------------
# Snowflake keep-alive defaults (configure_connection)
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_snowflake_keeps_its_session_alive_by_default(app1):
    """Without this every Snowflake process dies ~4h after boot with 390114."""
    _, conn = configure({
        'dialect': 'snowflake', 'account': 'A', 'database': 'D', 'schema': 'S',
        'warehouse': 'W', 'username': 'u', 'role': 'r',
    })
    assert conn.options['client_session_keep_alive'] is True

    # 900s, not the connector's 3600s default: it is clamped to [900, 3600] anyway, and a
    # heartbeat is a token-only REST call that burns no warehouse credits.
    assert conn.options['client_session_keep_alive_heartbeat_frequency'] == 900


@pytest.mark.asyncio
async def test_snowflake_keep_alive_defaults_do_not_clobber_app_config(app1):
    """.defaults() fills only what is missing - an app disabling keep-alive for a
    short-lived CLI, or picking its own heartbeat, must win."""
    _, conn = configure({
        'dialect': 'snowflake', 'account': 'A',
        'options': {
            'private_key': 'pk',
            'client_session_keep_alive': False,
            'client_session_keep_alive_heartbeat_frequency': 3600,
        },
    })
    assert conn.options['client_session_keep_alive'] is False
    assert conn.options['client_session_keep_alive_heartbeat_frequency'] == 3600
    assert conn.options['private_key'] == 'pk'      # existing options survive


@pytest.mark.asyncio
async def test_snowflake_keep_alive_does_not_leak_to_other_dialects(app1):
    """It is a Snowflake connect kwarg; asyncpg/aiomysql would reject it outright."""
    _, conn = configure({
        'dialect': 'postgresql', 'host': 'h', 'database': 'd', 'username': 'u', 'password': 'p',
    })
    assert 'client_session_keep_alive' not in (conn.get('options') or {})


# --------------------------------------------------------------------------
# database/snowflake.py - dead-session classifier
# --------------------------------------------------------------------------

# The real message shape, from a production log line.
REAL_390114 = (
    '(snowflake.connector.errors.ProgrammingError) 390114 (08001): None: '
    'Authentication token has expired.  The user must authenticate again.'
)


def test_the_real_production_message_is_recognized(app1):
    assert is_dead_session_error(Exception(REAL_390114)) is True


# Spelled out rather than read from the module: the point is to pin WHICH codes are
# terminal, so importing the module's own list would make the test tautological.
#   390110 ID_TOKEN_EXPIRED / 390113 MASTER_TOKEN_NOTFOUND
#   390114 MASTER_TOKEN_EXPIRED / 390115 MASTER_TOKEN_INVALID
@pytest.mark.parametrize('code', ['390110', '390113', '390114', '390115'])
def test_every_dead_session_code_is_recognized(app1, code):
    assert is_dead_session_error(Exception('{} (08001): token gone'.format(code))) is True


@pytest.mark.asyncio
async def test_the_terminal_code_list_is_exactly_those_four(app1):
    assert sf().DEAD_SESSION_CODES == ('390110', '390113', '390114', '390115')


def test_a_structured_errno_is_preferred_over_the_message(app1):
    """The connector sets .errno as an int; every wrapping layer reformats the message."""
    class Err(Exception):
        errno = 390114
    assert is_dead_session_error(Err('something entirely reworded')) is True


def test_a_wrapped_dbapi_error_is_unwrapped_via_orig(app1):
    """SQLAlchemy hands us its wrapper; the connector's errno lives on .orig."""
    class Orig(Exception):
        errno = 390114

    class Wrapper(Exception):
        orig = Orig('inner')

    assert is_dead_session_error(Wrapper('outer, reworded')) is True


def test_session_expired_390112_is_NOT_a_dead_session(app1):
    """The connector renews 390112 itself (network.py -> _renew_session), so treating it as
    a disconnect would throw away a pool that was about to heal on its own."""
    assert is_dead_session_error(Exception('390112 (08001): Session no longer exists.')) is False


def test_an_ordinary_sql_error_is_NOT_a_dead_session(app1):
    assert is_dead_session_error(
        Exception('001003 (42000): SQL compilation error: syntax error')) is False


def test_none_is_not_a_dead_session(app1):
    assert is_dead_session_error(None) is False


def test_digits_inside_a_data_value_do_not_trigger_it(app1):
    """Guard the regex anchor: bound data carries arbitrary numbers, and a false positive
    tears down a HEALTHY connection pool."""
    assert is_dead_session_error(
        Exception("Invalid value for column ro_number: '390114' is not a date")) is False


# --------------------------------------------------------------------------
# database/snowflake.py - the handle_error listener
# --------------------------------------------------------------------------

def fire(engine, exception, is_disconnect=False):
    """Run the engine's handle_error listeners against a stand-in ExceptionContext.

    SQLAlchemy's real ExceptionContext is not constructible standalone; the listener only
    touches .original_exception and .is_disconnect, which IS the contract - engine/base.py
    re-reads is_disconnect after the handler chain and, if it flipped to True, invalidates
    the connection and _invalidate()s the pool."""
    from types import SimpleNamespace
    ctx = SimpleNamespace(original_exception=exception, is_disconnect=is_disconnect)
    for fn in engine.dialect.dispatch.handle_error:
        fn(ctx)
    return ctx


def sqlite_engine():
    import sqlalchemy as sa
    return sa.create_engine('sqlite://')


def test_the_listener_flips_is_disconnect_for_a_dead_session(app1):
    engine = sqlite_engine()
    try:
        assert register_dead_session_recovery(engine) is True
        ctx = fire(engine, Exception(REAL_390114))
        assert ctx.is_disconnect is True, (
            'is_disconnect is the ONLY thing SQLAlchemy reads to decide whether to '
            'invalidate the pooled connection'
        )
    finally:
        engine.dispose()


def test_the_listener_leaves_an_unrelated_error_alone(app1):
    engine = sqlite_engine()
    try:
        register_dead_session_recovery(engine)
        ctx = fire(engine, Exception('001003 (42000): SQL compilation error'))
        assert ctx.is_disconnect is False
    finally:
        engine.dispose()


def test_arming_is_idempotent(app1):
    """Db.init() arms every snowflake engine it builds; a double-arm would double-log."""
    engine = sqlite_engine()
    try:
        assert register_dead_session_recovery(engine) is True
        assert register_dead_session_recovery(engine) is False
        assert len(list(engine.dialect.dispatch.handle_error)) == 1
    finally:
        engine.dispose()


def test_arming_is_scoped_to_one_engine(app1):
    """Attached per engine, NOT to the Engine class - a process holding a snowflake AND a
    postgres connection must only pay for it on the snowflake one."""
    armed, other = sqlite_engine(), sqlite_engine()
    try:
        register_dead_session_recovery(armed)
        assert len(list(armed.dialect.dispatch.handle_error)) == 1
        assert len(list(other.dialect.dispatch.handle_error)) == 0
    finally:
        armed.dispose()
        other.dispose()


def test_an_async_engine_is_armed_on_its_sync_engine(app1):
    """An AsyncEngine is a facade; events live on the sync engine underneath.  Snowflake has
    no async driver today, but the fix must not silently skip one that appears."""
    from sqlalchemy.ext.asyncio import create_async_engine
    engine = create_async_engine('sqlite+aiosqlite://')
    assert register_dead_session_recovery(engine) is True
    assert len(list(engine.sync_engine.dialect.dispatch.handle_error)) == 1


@pytest.mark.asyncio
async def test_init_arms_a_snowflake_engine(app1, monkeypatch):
    """The wiring: Db.init() must arm every snowflake engine it builds, automatically.

    snowflake-sqlalchemy is NOT a framework dependency - the DIALECT is supported here but
    the DRIVER is app-supplied - so a real snowflake engine cannot be constructed in this
    suite (sqlalchemy raises NoSuchModuleError).  We therefore stand in a sqlite engine for
    the driver only.  Everything actually under test - init() noticing
    dialect == 'snowflake' and arming the engine it just built - is uvicore's own code."""
    import sqlalchemy as sa
    from uvicore.typing import Dict
    from uvicore.contracts import Connection

    real_create_engine = sa.create_engine
    monkeypatch.setattr(sa, 'create_engine', lambda url, **kw: real_create_engine('sqlite://'))

    db = fresh_db()
    db.init('c', Dict({'c': Connection({
        'dialect': 'snowflake', 'account': 'A', 'database': 'D', 'schema': 'S',
        'warehouse': 'W', 'username': 'u', 'role': 'r',
    })}))
    engine = db.engine('c')

    assert len(list(engine.dialect.dispatch.handle_error)) == 1
    ctx = fire(engine, Exception(REAL_390114))
    assert ctx.is_disconnect is True


@pytest.mark.asyncio
async def test_init_does_not_arm_a_non_snowflake_engine(app1):
    """No cost, and no chance of a false positive, on the dialects that do not need it."""
    from uvicore.typing import Dict
    from uvicore.contracts import Connection

    db = fresh_db()
    db.init('c', Dict({'c': Connection({'dialect': 'sqlite', 'database': ':memory:'})}))
    engine = db.engine('c')
    assert len(list(engine.sync_engine.dialect.dispatch.handle_error)) == 0


# --------------------------------------------------------------------------
# End-to-end: the app1 reference app configures its own pool
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_app1_boots_with_an_app_configured_pool(app1):
    """app1's config/database.py sets a 'pool' block, so the whole suite boots a real app
    through this path rather than only exercising it from a unit test.  On sqlite that is
    pre_ping alone (StaticPool rejects size/max_overflow); the integration matrix runs the
    full block against real Postgres/MySQL/MariaDB."""
    import uvicore

    conn = uvicore.db.connection('app1')
    assert conn.pool['pre_ping'] is True

    engine = uvicore.db.engine('app1')
    sync_engine = getattr(engine, 'sync_engine', engine)
    assert sync_engine.pool._pre_ping is True
