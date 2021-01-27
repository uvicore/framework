import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_orm(app1):
    from app1.models.post import Post

    # Single NOT where like
    query = Post.query().where('body', '!like', '%favorite%')
    assert query.sql() == {'main': 'SELECT DISTINCT posts.id, posts.unique_slug, posts.title, posts.body, posts.other, posts.creator_id, posts.owner_id FROM posts WHERE posts.body NOT LIKE :body_1'}
    posts = await query.get()
    assert [1, 3, 5, 6, 7] == [x.id for x in posts]

    # Multiple NOT where like AND
    posts = await Post.query().where('body', '!like', '%favorite%').where('body', '!like', '%i lik%').get()
    assert [5, 6] == [x.id for x in posts]

    # Multiple NOT where like AND using a LIST
    posts = await Post.query().where([
        ('body', '!like', '%favorite%'),
        ('body', '!like', '%i lik%')
    ]).get()
    assert [5, 6] == [x.id for x in posts]

    # Where NOT like OR
    posts = await Post.query().or_where([
        ('body', '!like', '%I like%'),
        ('slug', '=', 'test-post1'),
    ]).get()
    assert [1, 2, 4, 5, 6] == [x.id for x in posts]

    # Where NOT like AND with where OR
    posts = await Post.query().where('body', '!like', '%like%').or_where([
        ('slug', 'test-post3'),
        ('slug', '=', 'test-post6'),
        ('slug', '=', 'test-post5'),
    ]).get()
    assert [5, 6] == [x.id for x in posts]


@pytest.mark.asyncio
async def Xtest_builder(app1):
    # FIXME, make it look exactly like the ORM version above
    pass


@pytest.mark.asyncio
async def Xtest_hybrid(app1):
    # FIXME, make it look exactly like the ORM version above
    pass


@pytest.mark.asyncio
async def Xtest_sqlalchemy(app1):
    # FIXME, make it look exactly like the ORM version above
    pass
