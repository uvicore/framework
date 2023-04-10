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
    # Single where IN
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id, 'in', [1, 2]).get()
    assert [1, 2, 3, 4, 5] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_single_bexp(app1, Posts, post):
    # Single where IN - binary expression
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id.in_([1, 2])).get()
    assert [1, 2, 3,4, 5] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and(app1, Posts, post):
    # Multiple where IN
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id, 'in', [1, 2]).where(post.owner_id, 'in', [1, 99]).get()
    assert [3, 4] == [x.id for x in posts]

    # Where IN with AND
    posts = await uvicore.db.query().table(Posts.table).where(post.other, 'null').where(post.owner_id, 'in', [1, 4]).get()
    assert [4, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_bexp(app1, Posts, post):
    # Multiple where IN - binary expression
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id.in_([1, 2])).where(post.owner_id.in_([1, 99])).get()
    assert [3, 4] == [x.id for x in posts]

    # Where IN with AND - binary expression
    posts = await uvicore.db.query().table(Posts.table).where(post.other == None).where(post.owner_id.in_([1, 4])).get()
    assert [4, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_or(app1, Posts, post):
    # Where IN with AND OR
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id, 'in', [1, 2]).or_where([
        (post.unique_slug, 'test-post1'),
        (post.unique_slug, 'test-post6'),
    ]).get()
    assert [1] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_and_or_bexp(app1, Posts, post):
    # Where IN with AND OR - binary expression
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id.in_([1, 2])).or_where([
        (post.unique_slug == 'test-post1'),
        (post.unique_slug == 'test-post6'),
    ]).get()
    assert [1] == [x.id for x in posts]
