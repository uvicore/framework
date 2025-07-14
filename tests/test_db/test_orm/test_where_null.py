import pytest
import uvicore
from uvicore.support.dumper import dump

# DB ORM

@pytest.mark.asyncio
async def test_where_null(app1):
    # Single where null
    from app1.models.post import Post
    posts = await Post.query().where('other', 'null').get()
    dump(posts)

    #assert False
    # ---
    # other
    # =
    # null
    # ---
    assert ['test-post2', 'test-post4', 'test-post5', 'test-post7'] == [x.slug for x in posts]


@pytest.mark.asyncio
async def test_where_null_with_operator(app1):
    # Single where null
    from app1.models.post import Post
    posts = await Post.query().where('other', '=', 'null').get()
    dump(posts)

    #assert False
    # ---
    # other
    # =
    # null
    # ---
    assert ['test-post2', 'test-post4', 'test-post5', 'test-post7'] == [x.slug for x in posts]


@pytest.mark.asyncio
async def test_where_none(app1):
    # Single where null
    from app1.models.post import Post
    posts = await Post.query().where('other', None).get()
    dump(posts)

    #assert False
    # ---
    # other
    # =
    # None
    # ---
    assert ['test-post2', 'test-post4', 'test-post5', 'test-post7'] == [x.slug for x in posts]


@pytest.mark.asyncio
async def test_where_none_with_operator(app1):
    # Single where null
    from app1.models.post import Post
    posts = await Post.query().where('other', '=', None).get()
    dump(posts)

    #assert False
    # ---
    # other
    # =
    # None
    # ---
    assert ['test-post2', 'test-post4', 'test-post5', 'test-post7'] == [x.slug for x in posts]

