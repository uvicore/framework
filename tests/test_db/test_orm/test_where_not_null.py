import pytest
import uvicore
from uvicore.support.dumper import dump

# DB ORM

@pytest.mark.asyncio
async def Xtest_where_not_null(app1):
    # Single where null
    from app1.models.post import Post
    posts = await Post.query().where('other', '!=', 'null').get()
    dump(posts)
    #sql = Post.query().where('other', '!=', 'null').sql() # IS NOT NULL
    #dump(sql)

    #assert False
    # ---
    # other
    # !=
    # null
    # ---
    assert ['test-post1', 'test-post3', 'test-post6'] == [x.slug for x in posts]


@pytest.mark.asyncio
async def test_where_none(app1):
    # Single where null
    from app1.models.post import Post
    posts = await Post.query().where('other', '!=', None).get()
    dump(posts)
    #sql = Post.query().where('other', '!=', None).sql() # IS NOT NULL
    #dump(sql)

    #assert False
    # ---
    # other
    # !=
    # None
    # ---
    assert ['test-post1', 'test-post3', 'test-post6'] == [x.slug for x in posts]
