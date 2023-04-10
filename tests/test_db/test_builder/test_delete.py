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

    # Check comments
    post = await Post.query().include('comments').find(slug='test-post8')
    assert len(post.comments) == 2

    # Delete post comments
    comments = await uvicore.db.query().table('comments').where('post_id', post.id).delete()
    post = await Post.query().include('comments').find(slug='test-post8')
    assert post.comments == None

    # Delete post
    await uvicore.db.query().table('posts').where('id', post.id).delete()

    # Check normal seeded posts
    seeded_posts = ['test-post1', 'test-post2', 'test-post3', 'test-post4', 'test-post5', 'test-post6', 'test-post7'];
    posts = await Post.query().get()
    assert(len(posts) == 7)
    assert(seeded_posts == [x.slug for x in posts])
