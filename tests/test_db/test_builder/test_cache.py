import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

# NOTE: default cache store in config/app.py should be redis

@pytest.mark.asyncio
async def test_cache_default_store(app1):
    cache_key = 'uvicore.database/test-hashtags-cache'
    hashtags = (await uvicore.db.query()
        .table('hashtags')
        .cache('test-hashtags-cache')
        .get()
    )
    # Should be in default store
    from_cache = await uvicore.cache.get(cache_key)
    assert [1, 2, 3, 4, 5] == [x.id for x in from_cache]

    # Should NOT be in array store
    from_otherstore = await uvicore.cache.store('array').get(cache_key)
    assert from_otherstore is None

    # Remove from cache for next tests
    await uvicore.cache.forget(cache_key)


@pytest.mark.asyncio
async def test_cache_array_store(app1):
    cache_key = 'uvicore.database/test-hashtags-cache'
    hashtags = (await uvicore.db.query()
        .table('hashtags')
        .cache('test-hashtags-cache', store='array')
        .get()
    )
    # Should bein array store
    from_cache = await uvicore.cache.store('array').get(cache_key)
    assert [1, 2, 3, 4, 5] == [x.id for x in from_cache]

    # Should not be in redis store
    from_otherstore = await uvicore.cache.store('redis').get(cache_key)
    assert from_otherstore is None

    # Remove from cache for next tests
    await uvicore.cache.store('array').forget(cache_key)


@pytest.mark.asyncio
async def test_cache_generated_hashkey(app1):
    # Generated has key for this query is c0a54e3e4c5e0620776e1f24651bdaaace3962de
    cache_key = 'uvicore.database/c0a54e3e4c5e0620776e1f24651bdaaace3962de'
    hashtags = (await uvicore.db.query()
        .table('hashtags')
        .cache()
        .get()
    )
    # Should be in default store
    from_cache = await uvicore.cache.get(cache_key)
    assert [1, 2, 3, 4, 5] == [x.id for x in from_cache]

    # Remove from cache for next tests
    await uvicore.cache.forget(cache_key)


@pytest.mark.asyncio
async def test_cache_hit(app1):
    cache_key = 'uvicore.database/test-hashtags-cache'
    await uvicore.cache.forget(cache_key)

    # Query once to set cache
    hashtags = (await uvicore.db.query()
        .table('hashtags')
        .cache('test-hashtags-cache')
        .get()
    )

    # Query again to HIT the cache
    hashtags2 = (await uvicore.db.query()
        .table('hashtags')
        .cache('test-hashtags-cache')
        .get()
    )
    assert [1, 2, 3, 4, 5] == [x.id for x in hashtags2]
    assert hashtags == hashtags2
