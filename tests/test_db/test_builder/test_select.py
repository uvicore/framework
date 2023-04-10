import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

@pytest.mark.asyncio
async def test_select_all(app1):
    posts = (await uvicore.db.query()
        .table('posts')
        .get()
    )
    dump(posts)
    assert [
        'test-post1',
        'test-post2',
        'test-post3',
        'test-post4',
        'test-post5',
        'test-post6',
        'test-post7'
    ] == [x.unique_slug for x in posts]


@pytest.mark.asyncio
async def test_select_one(app1):
    post = (await uvicore.db.query('app1')
        .table('posts')
        .find(2)
    )
    assert post.unique_slug == 'test-post2'
