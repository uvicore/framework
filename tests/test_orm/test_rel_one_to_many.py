import pytest
import uvicore
from uvicore.support.dumper import dump, dd


@pytest.mark.asyncio
async def test_one_to_many(app1):
    #from uvicore.auth.models.user import User
    from app1.models.post import Post
    #from app1.models.comment import Comment

    # One Post has Many Comments
    post = await Post.query().include('comments').find(1)
    assert [
        'Post1 Comment1',
        'Post1 Comment2'
    ] == [x.title for x in post.comments]


@pytest.mark.asyncio
async def test_one_to_many_inverse(app1):
    from uvicore.auth.models.user import User
    from app1.models.post import Post
    from app1.models.comment import Comment

    # Many Posts have one Creator (Inverse of One-To-Many)
    posts = await Post.query().include('creator').get()
    dump(posts)
    assert [
        'administrator@example.com',
        'administrator@example.com',
        'manager1@example.com',
        'manager1@example.com',
        'manager1@example.com',
        'user2@example.com',
        'user2@example.com',
    ] == [x.creator.email for x in posts]

    # Many Posts have One Comment (Inverse of One-To-Many)
    comments = await Comment.query().include('post').get()
    dump(comments)
    assert [
        'test-post1',
        'test-post1',
        'test-post3',
        'test-post3',
        'test-post3',
    ] == [x.post.slug for x in comments]
