import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump
from tests.seeders import seed_post8

# DB ORM


@pytest.mark.asyncio
async def test_single_instance(app1):
    # Delete single from instance.delete()
    from app1.models.post import Post

    # Normal seeded posts before any creation
    seeded_posts = ['test-post1', 'test-post2', 'test-post3', 'test-post4', 'test-post5', 'test-post6', 'test-post7'];

    # Check normal seeded posts
    posts = await Post.query().get()
    assert(len(posts) == 7)
    assert(seeded_posts == [x.slug for x in posts])

    # Create a temp post we can delete
    await seed_post8()

    # Check new posts
    posts = await Post.query().get()
    new_posts = seeded_posts.copy()
    new_posts.extend(['test-post8'])
    assert(new_posts == [x.slug for x in posts])

    # Delete single from an instance
    post = await Post.query().find(slug='test-post8')
    await post.delete()

    # Check normal seeded posts
    posts = await Post.query().get()
    assert(seeded_posts == [x.slug for x in posts])


@pytest.mark.asyncio
async def test_multi_query(app1):
    # Delete from where query
    from app1.models.post import Post, Comment

    # Create a temp post with 2 comments
    await seed_post8()

    # Check new post with 2 comments
    post = await Post.query().include('comments').find(slug='test-post8')
    assert len(post.comments) == 2

    # Delete comments with query
    await Comment.query().where('post_id', post.id).delete()

    # Check new post with 0 comments
    post = await Post.query().include('comments').find(slug='test-post8')
    assert post.comments == None

    # Delete post
    await Post.query().where('id', post.id).delete()

    # Check normal seeded posts
    seeded_posts = ['test-post1', 'test-post2', 'test-post3', 'test-post4', 'test-post5', 'test-post6', 'test-post7'];
    posts = await Post.query().get()
    assert(len(posts) == 7)
    assert(seeded_posts == [x.slug for x in posts])


