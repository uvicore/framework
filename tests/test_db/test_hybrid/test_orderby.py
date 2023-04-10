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
async def test_order_by_string_direction(app1, Posts, post):
    posts = (await uvicore.db.query()
        .table(Posts.table)

        # Order by with string based direction
        .order_by(post.id, 'DESC')

        .get()
    )
    dump(posts)
    assert [
        'test-post7',
        'test-post6',
        'test-post5',
        'test-post4',
        'test-post3',
        'test-post2',
        'test-post1'
    ] == [x.unique_slug for x in posts]


@pytest.mark.asyncio
async def test_order_by_unary_direction(app1, Posts, post):
    posts = (await uvicore.db.query()
        .table(Posts.table)

        # Order by with UnaryExpression based direction
        .order_by(sa.desc(post.id))

        .get()
    )
    dump(posts)
    assert [
        'test-post7',
        'test-post6',
        'test-post5',
        'test-post4',
        'test-post3',
        'test-post2',
        'test-post1'
    ] == [x.unique_slug for x in posts]
