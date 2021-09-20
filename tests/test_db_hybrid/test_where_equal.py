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
    yield Posts.table.c


@pytest.mark.asyncio
async def test_single(app1, Posts, post):
    # Single where
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id, 2).get()
    assert [3, 4, 5] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_single_bexp(app1, Posts, post):
    # Single where - binary expression
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id == 2).get()
    assert [3, 4, 5] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and(app1, Posts, post):
    # Multiple where AND
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id, '=', 2).where(post.owner_id, 1).get()
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_bexp(app1, Posts, post):
    # Multiple where AND - binary expression
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id == 2).where(post.owner_id == 1).get()
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_list(app1, Posts, post):
    # Multiple where AND using a LIST
    posts = await uvicore.db.query().table(Posts.table).where([
        (post.creator_id, '=', 2),
        (post.owner_id, 1),
    ]).get()
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_list_bexp(app1, Posts, post):
    # Multiple where AND using a LIST - binary expression
    posts = await uvicore.db.query().table(Posts.table).where([
        post.creator_id == 2,
        post.owner_id == 1
    ]).get()
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_or(app1, Posts, post):
    # Where OR
    posts = await uvicore.db.query().table(Posts.table).or_where([
        (post.unique_slug, 'test-post3'),
        (post.unique_slug, '=', 'test-post4'),
    ]).get()
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_or_bexp(app1, Posts, post):
    # Where OR - binary expression
    posts = await uvicore.db.query().table(Posts.table).or_where([
        post.unique_slug == 'test-post3',
        post.unique_slug == 'test-post4',
    ]).get()
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_or(app1, Posts, post):
    # Where AND with where OR
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id, '=', 2).or_where([
        (post.unique_slug, 'test-post3'),
        (post.unique_slug, '=', 'test-post4'),
    ]).get()
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_or_bexp(app1, Posts, post):
    # Where AND with where OR - binary expression
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id == 2).or_where([
        post.unique_slug == 'test-post3',
        post.unique_slug == 'test-post4',
    ]).get()
    assert [3, 4] == [x.id for x in posts]
