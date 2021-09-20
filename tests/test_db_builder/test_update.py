import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump
from tests.seeders import seed_post8

# DB Builder

@pytest.mark.asyncio
async def test_multi(app1):
    from app1.models import Post

    # Create a temp post with 2 comments
    await seed_post8()

    # Check original post
    post = await Post.query().include('comments').find(slug='test-post8')
    assert [
        'Body for post8 comment1',
        'Body for post8 comment2'
    ] == [x.body for x in post.comments]

    # Bulk update using where
    await uvicore.db.query().table('comments').where('post_id', post.id).update(body='new body')

    # Check updated post
    post = await Post.query().include('comments').find(slug='test-post8')
    assert [
        'new body',
        'new body'
    ] == [x.body for x in post.comments]

    # Delete temp post
    await uvicore.db.query().table('posts').where('id', post.id).delete()
