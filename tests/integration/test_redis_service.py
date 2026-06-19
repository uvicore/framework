"""
End-to-end integration tests for the generic `uvicore.redis` SERVICE.

This is NOT about caching (see test_redis_cache.py for the cache backend).  The
redis service (uvicore/redis/redis.py) is a thin connection helper + passthrough:
it resolves named connections from config, builds their URLs, lazily opens (and
caches) one `redis.asyncio` pool per connection URL, and hands back the raw async
redis client for callers to use directly.

So these tests verify two things against a REAL redis server:
  1. Connection management - default selection, named lookup, URL building,
     one cached engine per URL, and database-level isolation between connections.
  2. The passthrough itself - a representative slice of real redis commands
     (strings, counters, expiry, hashes, lists, sets, key scans) actually work
     through the returned client.

The service singleton is reached via `from uvicore.redis import Redis` - the
`@uvicore.service(singleton=True)` decorator swaps the bound instance into that
name (note `uvicore.redis` itself is the *module*, not the service).

Runs for real under `poetry run ./bin/test-redis-integration.sh`; when no redis
server is reachable the whole module SKIPS (via the `redis` fixture), so it is
harmless under the plain ./bin/test.sh unit run.

app1 defines two redis connections: 'app1' (database 0, the default) and 'cache'
(database 2) - see tests/apps/app1/config/database.py.
"""
import pytest
import pytest_asyncio
import uvicore
import redis.asyncio as aioredis

try:
    from redis.exceptions import RedisError
except ImportError:  # pragma: no cover - redis extra always present in tests
    RedisError = Exception


# All test keys share this prefix so cleanup never touches unrelated data on a
# shared/local redis (the service has no key-prefixing of its own).
KEY_PREFIX = 'uvicore-redis-itest:'


def k(name: str) -> str:
    return KEY_PREFIX + name


async def _cleanup(service):
    """Delete only this suite's keys, across every configured connection."""
    for name in service.connections.keys():
        client = await service.connect(name)
        keys = await client.keys(KEY_PREFIX + '*')
        if keys:
            await client.delete(*keys)


@pytest_asyncio.fixture(loop_scope="session")
async def redis(app1):
    """The redis service singleton, auto-skipped when no server is reachable.

    `redis.asyncio.from_url` is lazy, so the first command (ping) is what really
    opens the socket - if that fails the whole module skips instead of erroring.

    loop_scope="session" pins this fixture to the same session event loop the
    tests and the session-scoped `app1` fixture use.  Without it, pytest-asyncio
    runs a function-scoped async fixture in its OWN loop, the redis connection
    pool binds to that loop, and every test then fails with "Future attached to a
    different loop" when it reuses the cached pool.
    """
    from uvicore.redis import Redis as service
    try:
        client = await service.connect()
        await client.ping()
    except (RedisError, OSError) as e:
        pytest.skip(f'redis not reachable for redis service integration tests: {e}')
    await _cleanup(service)
    yield service
    await _cleanup(service)


# --------------------------------------------------------------------------
# Service wiring / configuration
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_service_is_bound_singleton(redis):
    """`from uvicore.redis import Redis` is the same instance the IoC resolves."""
    assert redis is uvicore.ioc.make('uvicore.redis.redis.Redis')


@pytest.mark.asyncio
async def test_default_connection_is_app1(redis):
    assert redis.default == 'app1'


@pytest.mark.asyncio
async def test_connections_are_registered(redis):
    assert set(redis.connections.keys()) == {'app1', 'cache'}


@pytest.mark.asyncio
async def test_connection_url_is_built_from_parts(redis):
    """init() composes redis://host:port/database for each connection."""
    for name in ('app1', 'cache'):
        conn = redis.connection(name)
        assert conn.url == f'redis://{conn.host}:{conn.port}/{conn.database}'
    # The two connections target different logical databases
    assert redis.connection('app1').database != redis.connection('cache').database


@pytest.mark.asyncio
async def test_connection_without_name_returns_default(redis):
    assert redis.connection().url == redis.connection('app1').url


@pytest.mark.asyncio
async def test_unknown_connection_raises(redis):
    with pytest.raises(Exception) as exc:
        redis.connection('does-not-exist')
    assert 'does-not-exist' in str(exc.value)


# --------------------------------------------------------------------------
# Connect / engine pooling
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_connect_returns_async_client(redis):
    client = await redis.connect()
    assert isinstance(client, aioredis.Redis)
    assert await client.ping() is True


@pytest.mark.asyncio
async def test_engine_is_cached_per_url(redis):
    """connect() reuses one pool per URL - default resolves to the app1 pool."""
    a = await redis.connect('app1')
    b = await redis.connect('app1')
    default = await redis.connect()
    assert a is b
    assert a is default


@pytest.mark.asyncio
async def test_distinct_connections_use_distinct_engines(redis):
    app1 = await redis.connect('app1')
    cache = await redis.connect('cache')
    assert app1 is not cache


@pytest.mark.asyncio
async def test_engine_registered_after_connect(redis):
    await redis.connect('app1')
    assert redis.connection('app1').url in redis.engines


# --------------------------------------------------------------------------
# Passthrough: strings
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_set_get_delete(redis):
    client = await redis.connect()
    assert await client.set(k('str'), 'hello') is True
    assert await client.get(k('str')) == b'hello'
    assert await client.exists(k('str')) == 1
    assert await client.delete(k('str')) == 1
    assert await client.get(k('str')) is None


@pytest.mark.asyncio
async def test_setnx_and_append(redis):
    client = await redis.connect()
    assert await client.setnx(k('nx'), 'first') is True
    assert await client.setnx(k('nx'), 'second') is False     # already present
    assert await client.get(k('nx')) == b'first'
    await client.append(k('nx'), '!')
    assert await client.get(k('nx')) == b'first!'
    assert await client.strlen(k('nx')) == 6


@pytest.mark.asyncio
async def test_counters(redis):
    client = await redis.connect()
    assert await client.incr(k('n')) == 1
    assert await client.incr(k('n')) == 2
    assert await client.incrby(k('n'), 5) == 7
    assert await client.decr(k('n')) == 6
    assert await client.decrby(k('n'), 4) == 2


@pytest.mark.asyncio
async def test_mset_mget(redis):
    client = await redis.connect()
    await client.mset({k('m1'): 'a', k('m2'): 'b'})
    assert await client.mget(k('m1'), k('m2'), k('m-missing')) == [b'a', b'b', None]


# --------------------------------------------------------------------------
# Passthrough: expiry / TTL
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_expire_and_ttl(redis):
    client = await redis.connect()
    await client.set(k('ttl'), 'v')
    assert await client.ttl(k('ttl')) == -1          # no expiry yet
    assert await client.expire(k('ttl'), 100) is True
    assert 0 < await client.ttl(k('ttl')) <= 100
    assert await client.persist(k('ttl')) is True
    assert await client.ttl(k('ttl')) == -1          # expiry removed


@pytest.mark.asyncio
async def test_setex(redis):
    client = await redis.connect()
    await client.setex(k('sx'), 100, 'v')
    assert await client.get(k('sx')) == b'v'
    assert 0 < await client.ttl(k('sx')) <= 100


# --------------------------------------------------------------------------
# Passthrough: hashes / lists / sets
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_hash_ops(redis):
    client = await redis.connect()
    await client.hset(k('h'), 'field1', 'v1')
    await client.hset(k('h'), mapping={'field2': 'v2', 'field3': 'v3'})
    assert await client.hget(k('h'), 'field1') == b'v1'
    assert await client.hgetall(k('h')) == {b'field1': b'v1', b'field2': b'v2', b'field3': b'v3'}
    assert await client.hlen(k('h')) == 3
    assert await client.hdel(k('h'), 'field1') == 1
    assert await client.hexists(k('h'), 'field1') is False


@pytest.mark.asyncio
async def test_list_ops(redis):
    client = await redis.connect()
    assert await client.rpush(k('l'), 'a', 'b', 'c') == 3
    await client.lpush(k('l'), 'z')
    assert await client.lrange(k('l'), 0, -1) == [b'z', b'a', b'b', b'c']
    assert await client.llen(k('l')) == 4
    assert await client.lpop(k('l')) == b'z'
    assert await client.rpop(k('l')) == b'c'


@pytest.mark.asyncio
async def test_set_ops(redis):
    client = await redis.connect()
    assert await client.sadd(k('s'), 'x', 'y', 'z') == 3
    assert await client.sadd(k('s'), 'x') == 0          # duplicate, not added
    assert await client.scard(k('s')) == 3
    assert await client.sismember(k('s'), 'y')          # member (1/True)
    assert not await client.sismember(k('s'), 'absent') # non-member (0/False)
    assert await client.smembers(k('s')) == {b'x', b'y', b'z'}
    assert await client.srem(k('s'), 'y') == 1


@pytest.mark.asyncio
async def test_keys_pattern_scan(redis):
    client = await redis.connect()
    await client.mset({k('scan:1'): '1', k('scan:2'): '2', k('other'): '3'})
    found = await client.keys(k('scan:*'))
    assert {key.decode() for key in found} == {k('scan:1'), k('scan:2')}


# --------------------------------------------------------------------------
# Connections are isolated by logical database
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_connections_are_isolated_by_database(redis):
    app1 = await redis.connect('app1')      # database 0
    cache = await redis.connect('cache')    # database 2

    await app1.set(k('only-on-app1'), 'a')
    await cache.set(k('only-on-cache'), 'c')

    # Each key is visible only on the database it was written to
    assert await app1.exists(k('only-on-app1')) == 1
    assert await cache.exists(k('only-on-app1')) == 0
    assert await cache.exists(k('only-on-cache')) == 1
    assert await app1.exists(k('only-on-cache')) == 0
