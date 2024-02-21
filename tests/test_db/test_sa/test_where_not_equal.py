import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB SQLAlchemy

@pytest.fixture(scope="module")
def Posts():
    from app1.database.tables.posts import Posts
    yield Posts


@pytest.fixture(scope="module")
def post(Posts):
    yield Posts.table


@pytest.mark.asyncio
async def test_single(app1, Posts, post):
    # Single NOT where
    query = post.select().where(post.c.creator_id != 2).order_by('id')
    posts = await uvicore.db.fetchall(query, connection='app1')
    assert [1, 2, 6, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and(app1, Posts, post):
    # Multiple where NOT AND
    query = post.select().where(post.c.creator_id != 2).where(post.c.owner_id != 2).order_by('id')
    posts = await uvicore.db.fetchall(query)
    assert [6, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and2(app1, Posts, post):
    # Multiple where NOT AND using multiple parameters on and_
    query = post.select().where(sa.and_(post.c.creator_id != 2, post.c.owner_id != 2)).order_by('id')
    posts = await uvicore.db.fetchall(query)
    assert [6, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_or(app1, Posts, post):
    # Where NOT OR
    query = post.select().where(sa.or_(post.c.creator_id != 1, post.c.owner_id != 2)).order_by('id')
    posts = await uvicore.db.fetchall(query)
    assert [3, 4, 5, 6, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_or(app1, Posts, post):
    # Where NOT AND with where OR
    query = post.select().where(post.c.unique_slug != 'test-post5').where(sa.or_(post.c.creator_id != 1, post.c.owner_id != 2)).order_by('id')
    posts = await uvicore.db.fetchall(query)
    assert [3, 4, 6, 7] == [x.id for x in posts]
