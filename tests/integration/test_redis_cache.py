"""
End-to-end integration tests for the REDIS cache backend.

The default unit suite (`poetry run ./bin/test.sh`) exercises the in-memory
`array` cache backend (CACHE_STORE defaults to 'array' in app1's cache config).
This module talks to the **redis** cache store explicitly via
`uvicore.cache.store('redis')`, so it verifies the real redis backend regardless
of which store is configured as the default.

It runs for real under `poetry run ./bin/test-cache-integration.sh`, which brings
up a throwaway redis container and points the cache 'redis' store at it (see
tests/integration/env/redis.env).  When no redis server is reachable - e.g. the
plain SQLite unit run with no redis available - every test in this module SKIPS
(via the `cache` fixture) instead of failing, exactly like the cross-db suite
runs harmlessly against SQLite by default.

The redis backend pickle-serializes values, so arbitrary python objects must
round-trip, and it stores keys under the configured prefix ('app1::cache/').
"""
import asyncio
import pytest
import pytest_asyncio
import uvicore

try:
    from redis.exceptions import RedisError
except ImportError:  # pragma: no cover - redis extra always present in tests
    RedisError = Exception


@pytest_asyncio.fixture(loop_scope="session")
async def cache(app1):
    """Function-scoped redis cache store, isolated and auto-skipped.

    Resolves the 'redis' cache store (not the configured default) so these tests
    always exercise the redis backend.  `redis.asyncio.from_url` is lazy, so the
    first command is what actually opens the socket - if that fails (no redis
    server), the whole test skips rather than erroring.  flush() before and after
    keeps each test isolated; flush only touches keys under the cache prefix.

    loop_scope="session" pins this fixture to the same session event loop the
    tests run in (matching the session-scoped `app1` fixture).  Without it,
    pytest-asyncio runs a function-scoped async fixture in its OWN loop, the
    redis connection pool binds to that loop, and every test then fails with
    "Future attached to a different loop" when it reuses the cached pool.
    """
    store = uvicore.cache.store('redis')
    try:
        await store.flush()
    except (RedisError, OSError) as e:
        pytest.skip(f'redis not reachable for cache integration tests: {e}')
    yield store
    try:
        await store.flush()
    except (RedisError, OSError):
        pass


async def raw_redis():
    """The underlying aioredis connection behind the 'cache' store, for asserting
    on what physically landed in redis (prefixes, TTLs, untouched foreign keys)."""
    from uvicore.redis import Redis as RedisDb
    return await RedisDb.connect('cache')


# --------------------------------------------------------------------------
# Wiring / connectivity
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_store_is_redis_backend(cache):
    """uvicore.cache.store('redis') resolves the redis driver, not the array one."""
    assert cache.__class__.__module__ == 'uvicore.cache.backends.redis'
    assert cache.__class__.__name__ == 'Redis'
    assert cache.prefix  # a non-empty key prefix is configured


# --------------------------------------------------------------------------
# Core put / get / has
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_put_and_get(cache):
    await cache.put('greeting', 'hello', seconds=3600)
    assert await cache.get('greeting') == 'hello'
    assert await cache.has('greeting') is True


@pytest.mark.asyncio
async def test_get_missing_returns_default(cache):
    assert await cache.get('nope') is None
    assert await cache.get('nope', default='fallback') == 'fallback'
    assert await cache.has('nope') is False


@pytest.mark.asyncio
async def test_put_get_multiple(cache):
    """Dict put + list get round-trips, keyed by the un-prefixed names."""
    await cache.put({'a': 1, 'b': 2}, seconds=3600)
    got = await cache.get(['a', 'b', 'c'], default='NA')
    assert got['a'] == 1
    assert got['b'] == 2
    assert got['c'] == 'NA'  # missing key falls back to default


# --------------------------------------------------------------------------
# forget / pull / add
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_forget_single_and_list(cache):
    await cache.put({'k1': 'v1', 'k2': 'v2', 'k3': 'v3'}, seconds=3600)
    await cache.forget('k1')
    assert await cache.has('k1') is False
    await cache.forget(['k2', 'k3'])
    assert await cache.has('k2') is False
    assert await cache.has('k3') is False


@pytest.mark.asyncio
async def test_pull_returns_then_removes(cache):
    await cache.put('once', 'value', seconds=3600)
    assert await cache.pull('once') == 'value'
    assert await cache.has('once') is False


@pytest.mark.asyncio
async def test_add_only_when_absent(cache):
    assert await cache.add('addkey', 'first', seconds=3600) is True
    assert await cache.add('addkey', 'second', seconds=3600) is False
    assert await cache.get('addkey') == 'first'  # original value untouched


# --------------------------------------------------------------------------
# remember
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_remember_runs_callback_only_on_miss(cache):
    calls = {'n': 0}

    async def compute():
        calls['n'] += 1
        return 'computed'

    assert await cache.remember('rk', compute, seconds=3600) == 'computed'
    assert calls['n'] == 1
    # Second call is a cache hit -> callback must not run again
    assert await cache.remember('rk', compute, seconds=3600) == 'computed'
    assert calls['n'] == 1


@pytest.mark.asyncio
async def test_remember_with_plain_value(cache):
    assert await cache.remember('rk2', 'plain', seconds=3600) == 'plain'
    assert await cache.get('rk2') == 'plain'


# --------------------------------------------------------------------------
# increment / decrement
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_increment_and_decrement(cache):
    assert await cache.increment('counter') == 1       # creates at 1
    assert await cache.increment('counter') == 2
    assert await cache.increment('counter', 5) == 7
    assert await cache.decrement('counter', 3) == 4
    assert await cache.decrement('counter') == 3


# --------------------------------------------------------------------------
# Serialization - arbitrary python objects must survive the pickle round-trip
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_complex_value_roundtrip(cache):
    data = {
        'nested': {'a': [1, 2, 3], 'b': {'c': True}},
        'tuple': (1, 'two', 3.0),
        'list': [{'x': 1}, {'y': 2}],
        'none': None,
        'num': 42,
    }
    await cache.put('complex', data, seconds=3600)
    got = await cache.get('complex')
    assert got == data
    assert isinstance(got['tuple'], tuple)  # tuple stays a tuple, not a list


# --------------------------------------------------------------------------
# TTL / expiry - the real redis server enforces expiration
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_ttl_expiry(cache):
    await cache.put('ephemeral', 'soon-gone', seconds=1)
    assert await cache.get('ephemeral') == 'soon-gone'
    await asyncio.sleep(1.3)
    assert await cache.has('ephemeral') is False
    assert await cache.get('ephemeral') is None


@pytest.mark.asyncio
async def test_touch_resets_ttl(cache):
    await cache.put('touchme', 'v', seconds=100)
    assert await cache.touch('touchme', seconds=5) is True
    assert await cache.touch('does-not-exist') is False
    raw = await raw_redis()
    ttl = await raw.ttl(cache.prefix + 'touchme')
    assert 0 < ttl <= 5  # TTL was reset down to the new 5s window


# --------------------------------------------------------------------------
# Physical redis behavior - prefixing and prefix-scoped flush
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_keys_are_stored_with_prefix(cache):
    await cache.put('prefixed', 'val', seconds=3600)
    raw = await raw_redis()
    # Key physically exists under the configured prefix in redis...
    assert await raw.exists(cache.prefix + 'prefixed') == 1
    # ...and not under the bare, un-prefixed name.
    assert await raw.exists('prefixed') == 0


@pytest.mark.asyncio
async def test_flush_only_removes_prefixed_keys(cache):
    raw = await raw_redis()
    foreign = 'integration-foreign-key-not-a-cache-entry'
    await raw.set(foreign, b'keep-me')
    try:
        await cache.put('inside', 'v', seconds=3600)
        await cache.flush()
        # Our cache key is gone...
        assert await cache.get('inside') is None
        # ...but the unrelated, non-prefixed key is left untouched.
        assert await raw.get(foreign) == b'keep-me'
    finally:
        await raw.delete(foreign)


# --------------------------------------------------------------------------
# Multiple stores are independent backends
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_redis_and_array_stores_are_independent(cache):
    array = uvicore.cache.store('array')
    await cache.put('shared', 'from-redis', seconds=3600)
    await array.put('shared', 'from-array', seconds=3600)
    try:
        assert await cache.get('shared') == 'from-redis'
        assert await array.get('shared') == 'from-array'
    finally:
        await array.forget('shared')
