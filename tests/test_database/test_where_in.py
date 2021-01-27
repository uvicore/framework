import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_orm(app1):
    from app1.models.post import Post

    # Single where IN
    posts = await Post.query().where('creator_id', 'in', [1, 2]).get()
    assert [1, 2, 3, 4, 5] == [x.id for x in posts]

    # Multiple where IN
    posts = await Post.query().where('creator_id', 'in', [1, 2]).where('owner_id', 'in', [1, 99]).get()
    assert [3, 4] == [x.id for x in posts]

    # Where IN with AND
    posts = await Post.query().where('other', 'null').where('owner_id', 'in', [1, 4]).get()
    assert [4, 7] == [x.id for x in posts]

    # Where IN with AND OR
    posts = await Post.query().where('creator_id', 'in', [1, 2]).or_where([
        ('slug', 'test-post1'),
        ('slug', 'test-post6'),
    ]).get()
    assert [1] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_builder(app1):
    # Single where IN
    posts = await uvicore.db.query().table('posts').where('creator_id', 'in', [1, 2]).get()
    assert [1, 2, 3, 4, 5] == [x.id for x in posts]

    # Multiple where IN
    posts = await uvicore.db.query().table('posts').where('creator_id', 'in', [1, 2]).where('owner_id', 'in', [1, 99]).get()
    assert [3, 4] == [x.id for x in posts]

    # Where IN with AND
    posts = await uvicore.db.query().table('posts').where('other', 'null').where('owner_id', 'in', [1, 4]).get()
    assert [4, 7] == [x.id for x in posts]

    # Where IN with AND OR
    posts = await uvicore.db.query().table('posts').where('creator_id', 'in', [1, 2]).or_where([
        ('unique_slug', 'test-post1'),
        ('unique_slug', 'test-post6'),
    ]).get()
    assert [1] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_hybrid(app1):
    from app1.database.tables.posts import Posts
    post = Posts.table.c

    # Single where IN
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id, 'in', [1, 2]).get()
    assert [1, 2, 3, 4, 5] == [x.id for x in posts]

    # Single where IN - binary expression
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id.in_([1, 2])).get()
    assert [1, 2, 3,4, 5] == [x.id for x in posts]


    # Multiple where IN
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id, 'in', [1, 2]).where(post.owner_id, 'in', [1, 99]).get()
    assert [3, 4] == [x.id for x in posts]

    # Multiple where IN - binary expression
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id.in_([1, 2])).where(post.owner_id.in_([1, 99])).get()
    assert [3, 4] == [x.id for x in posts]

    # Where IN with AND
    posts = await uvicore.db.query().table(Posts.table).where(post.other, 'null').where(post.owner_id, 'in', [1, 4]).get()
    assert [4, 7] == [x.id for x in posts]

    # Where IN with AND - binary expression
    posts = await uvicore.db.query().table(Posts.table).where(post.other == None).where(post.owner_id.in_([1, 4])).get()
    assert [4, 7] == [x.id for x in posts]

    # Where IN with AND OR
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id, 'in', [1, 2]).or_where([
        (post.unique_slug, 'test-post1'),
        (post.unique_slug, 'test-post6'),
    ]).get()
    assert [1] == [x.id for x in posts]

    # Where IN with AND OR
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id.in_([1, 2])).or_where([
        (post.unique_slug == 'test-post1'),
        (post.unique_slug == 'test-post6'),
    ]).get()
    assert [1] == [x.id for x in posts]


@pytest.mark.asyncio
async def Xtest_sqlalchemy(app1):
    # FIXME, make it look exactly like the ORM version above
    pass
