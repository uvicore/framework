import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump
from tests.seeders import seed_post8, delete_post8

# DB ORM

@pytest.mark.asyncio
async def test_instance(app1):
    # Updates from instance.save()
    from app1.models.post import Post

    # Create a temp post with 2 comments
    await seed_post8()

    # Check original post
    post = await Post.query().include('comments').find(slug='test-post8')
    assert [
        'Body for post8 comment1',
        'Body for post8 comment2'
    ] == [x.body for x in post.comments]

    # Loop each post comment and .save()
    post = await Post.query().include('comments').find(slug='test-post8')
    for comment in post.comments:
        comment.body = 'new body'
        await comment.save()

    # Check updated post
    post = await Post.query().include('comments').find(slug='test-post8')
    assert [
        'new body',
        'new body'
    ] == [x.body for x in post.comments]

    # Delete data from seed_post8 and all children
    await delete_post8(post.id)


@pytest.mark.asyncio
async def test_instance(app1):
    # Updates using query
    from app1.models import Post, Comment

    # Create a temp post with 2 comments
    await seed_post8()

    # Check original post
    post = await Post.query().include('comments').find(slug='test-post8')
    assert [
        'Body for post8 comment1',
        'Body for post8 comment2'
    ] == [x.body for x in post.comments]

    # Bulk update using where
    await Comment.query().where('post_id', post.id).update(body='new body')

    # Check updated post
    post = await Post.query().include('comments').find(slug='test-post8')
    assert [
        'new body',
        'new body'
    ] == [x.body for x in post.comments]

    # Delete data from seed_post8 and all children
    await delete_post8(post.id)

