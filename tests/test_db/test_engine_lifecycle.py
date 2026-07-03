"""
Engine lifecycle for the database layer.

Db.init() may be called more than once at runtime (ex: an app re-inits to change a
snowflake warehouse).  A re-init must NOT blindly rebuild every engine: replacing an
engine orphans its old connection pool, which can never be disposed and leaks driver
connections that finalize after the event loop closes (RuntimeError: Event loop is
closed).  So init() reuses an engine whose URL is unchanged, disposes one it replaces,
and Db.disconnect() disposes everything at shutdown (wired to the console/http/pytest
Shutdown events by the database provider).
"""
import pytest


def fresh_db(cfg):
    import uvicore
    from uvicore.typing import Dict
    from uvicore.contracts import Connection
    db = type(uvicore.db)()           # fresh Db instance (no global engine side effects)
    connections = Dict({'c': Connection(cfg)})
    db.init('c', connections)
    return db, connections


def pool_of(engine):
    """The engine's current pool.  Engine.dispose() replaces the pool with a fresh
    empty one, so a changed pool identity proves dispose ran."""
    return engine.sync_engine.pool


@pytest.mark.asyncio
async def test_reinit_reuses_engine_when_url_unchanged(app1):
    db, connections = fresh_db({'dialect': 'sqlite', 'database': ':memory:'})
    metakey = connections['c'].metakey
    engine = db.engines[metakey]
    metadata = db.metadatas[metakey]

    db.init('c', connections)
    assert db.engines[metakey] is engine        # reused, not rebuilt
    assert db.metadatas[metakey] is metadata    # metadata (and its tables) preserved


@pytest.mark.asyncio
async def test_reinit_disposes_replaced_engine_when_url_changed(app1):
    import asyncio
    db, connections = fresh_db({'dialect': 'sqlite', 'database': ':memory:'})
    metakey = connections['c'].metakey
    old_engine = db.engines[metakey]
    old_pool = pool_of(old_engine)
    metadata = db.metadatas[metakey]

    # Same metakey, different URL (like a snowflake warehouse change)
    connections['c'].url = 'sqlite+aiosqlite:///file:lifecycle?mode=memory&cache=shared&uri=true'
    db.init('c', connections)
    await asyncio.sleep(0.05)                   # let the scheduled dispose task run

    assert db.engines[metakey] is not old_engine
    assert pool_of(old_engine) is not old_pool  # old engine disposed, not orphaned
    assert db.metadatas[metakey] is metadata    # metadata survives the engine swap


@pytest.mark.asyncio
async def test_disconnect_all_disposes_every_engine(app1):
    db, connections = fresh_db({'dialect': 'sqlite', 'database': ':memory:'})
    engine = db.engines[connections['c'].metakey]
    old_pool = pool_of(engine)

    await db.disconnect(all_dbs=True)
    assert pool_of(engine) is not old_pool


@pytest.mark.asyncio
async def test_disconnect_one_connection(app1):
    db, connections = fresh_db({'dialect': 'sqlite', 'database': ':memory:'})
    engine = db.engines[connections['c'].metakey]
    old_pool = pool_of(engine)

    await db.disconnect(connection='c')
    assert pool_of(engine) is not old_pool
