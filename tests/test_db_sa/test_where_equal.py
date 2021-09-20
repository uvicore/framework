import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Hybrid

@pytest.fixture(scope="module")
def Posts():
    from app1.database.tables.posts import Posts
    yield Posts


@pytest.fixture(scope="module")
def post(Posts):
    yield Posts.table


@pytest.mark.asyncio
async def test_single(app1, Posts, post):
    # Single where
    query = post.select().where(post.c.creator_id == 2)
    posts = await uvicore.db.fetchall(query, connection='app1')
    assert [3, 4, 5] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and(app1, Posts, post):
    # Multiple where AND
    query = post.select().where(post.c.creator_id == 2).where(post.c.owner_id == 1)
    posts = await uvicore.db.fetchall(query)
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and2(app1, Posts, post):
    # Multiple where AND using multiple parameters on and_
    query = post.select().where(sa.and_(post.c.creator_id == 2, post.c.owner_id == 1))
    posts = await uvicore.db.fetchall(query)
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_or(app1, Posts, post):
    # Where OR
    query = post.select().where(sa.or_(post.c.unique_slug == 'test-post3', post.c.unique_slug == 'test-post4'))
    posts = await uvicore.db.fetchall(query)
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_or(app1, Posts, post):
    # Where AND with where OR
    query = post.select().where(post.c.creator_id == 2).where(sa.or_(post.c.unique_slug == 'test-post3', post.c.unique_slug == 'test-post4'))
    posts = await uvicore.db.fetchall(query)
    assert [3, 4] == [x.id for x in posts]
