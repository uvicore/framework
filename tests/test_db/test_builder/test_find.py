import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

@pytest.mark.asyncio
async def test_find_pk(app1):
    post = (await uvicore.db.query().table('posts').find(1))
    assert post.unique_slug == 'test-post1'


@pytest.mark.asyncio
async def test_find_custom_column(app1):
    post = (await uvicore.db.query().table('posts').find(unique_slug='test-post1'))
    assert post.unique_slug == 'test-post1'


@pytest.mark.asyncio
async def test_find_no_results(app1):
    post = (await uvicore.db.query().table('posts').find(9999))
    assert post is None
