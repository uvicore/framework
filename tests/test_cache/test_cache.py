"""
Full Cache contract coverage for the in-memory `array` cache backend.

This is the default cache store for the unit suite (CACHE_STORE defaults to
'array' in tests/apps/app1/config/cache.py).  The matching redis backend is
covered end-to-end in tests/integration/test_redis_cache.py against a real redis
server; this module exercises the SAME contract against the array backend so the
two stay behaviorally aligned.

The array backend keeps python objects in a plain dict (no pickle), so values
round-trip by identity and TTLs are enforced lazily on access.
"""
import asyncio
import pytest
import pytest_asyncio
import uvicore


# Every method on the Cache contract (uvicore/contracts/cache.py).
CONTRACT_METHODS = [
    'connect', 'store', 'has', 'get', 'remember', 'put', 'pull',
    'add', 'touch', 'increment', 'decrement', 'forget', 'flush',
]


@pytest_asyncio.fixture
async def cache(app1):
    """Function-scoped array cache store, flushed before and after for isolation.

    Resolves the 'array' store explicitly (not the configured default) so this
    suite always exercises the array backend, even when CACHE_STORE is pointed at
    redis.  The array backend holds state in a process-local dict that lives for
    the whole session, so flush() on each side keeps tests independent.  No
    loop_scope juggling is needed here (unlike the redis fixture) because the
    array backend owns no event-loop-bound resources.
    """
    store = uvicore.cache.store('array')
    await store.flush()
    yield store
    await store.flush()


# --------------------------------------------------------------------------
# Service / wiring
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_cache_service_available(app1):
    assert hasattr(uvicore, 'cache'), "Cache service should be available"


@pytest.mark.asyncio
async def test_store_is_array_backend(cache):
    """uvicore.cache.store('array') resolves the array driver, not the redis one."""
    assert cache.__class__.__module__ == 'uvicore.cache.backends.array'
    assert cache.__class__.__name__ == 'Array'
    assert cache.prefix  # a non-empty key prefix is configured


@pytest.mark.asyncio
async def test_full_contract_surface(cache):
    """Every method declared on the Cache contract is implemented."""
    for method in CONTRACT_METHODS:
        assert hasattr(cache, method), f"array backend missing '{method}'"


@pytest.mark.asyncio
async def test_distinct_stores(cache):
    """The 'redis' store resolves to a different backend instance/class."""
    redis_store = uvicore.cache.store('redis')  # instantiation only, no connection
    assert redis_store.__class__.__name__ == 'Redis'
    assert redis_store is not cache


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
    # The running total is actually persisted between calls
    assert await cache.get('counter') == 3


# --------------------------------------------------------------------------
# Serialization - the array backend stores live python objects as-is
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
# TTL / expiry - the array backend expires lazily on access
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_ttl_expiry(cache):
    await cache.put('ephemeral', 'soon-gone', seconds=1)
    assert await cache.get('ephemeral') == 'soon-gone'
    await asyncio.sleep(1.2)
    assert await cache.has('ephemeral') is False
    assert await cache.get('ephemeral') is None


@pytest.mark.asyncio
async def test_put_zero_seconds_never_expires(cache):
    """seconds=0 means 'never expire' - no TTL is registered for the key."""
    await cache.put('forever', 'value', seconds=0)
    assert (cache.prefix + 'forever') not in cache.items_ttl
    assert await cache.get('forever') == 'value'


@pytest.mark.asyncio
async def test_touch_resets_ttl(cache):
    pk = cache.prefix + 'touchme'
    await cache.put('touchme', 'v', seconds=1000)
    high = cache.items_ttl[pk]
    assert await cache.touch('touchme', seconds=5) is True
    assert cache.items_ttl[pk] < high          # TTL was reset down to ~5s
    assert await cache.touch('does-not-exist') is False
    assert await cache.get('touchme') == 'v'   # value still present


# --------------------------------------------------------------------------
# Physical store behavior - prefixing and prefix-scoped flush
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_keys_are_stored_with_prefix(cache):
    await cache.put('prefixed', 'val', seconds=3600)
    # Key physically lives under the configured prefix in the backing dict...
    assert (cache.prefix + 'prefixed') in cache.items
    # ...and not under the bare, un-prefixed name.
    assert 'prefixed' not in cache.items


@pytest.mark.asyncio
async def test_flush_only_removes_prefixed_keys(cache):
    foreign = 'unit-foreign-key-not-a-cache-entry'
    cache.items[foreign] = 'keep-me'  # a key without the cache prefix
    try:
        await cache.put('inside', 'v', seconds=3600)
        await cache.flush()
        # Our cache key is gone...
        assert await cache.get('inside') is None
        # ...but the unrelated, non-prefixed key is left untouched.
        assert cache.items.get(foreign) == 'keep-me'
    finally:
        cache.items.pop(foreign, None)
