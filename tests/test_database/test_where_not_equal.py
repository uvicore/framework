import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_orm(app1):
    from app1.models.post import Post

    # Single where
    posts = await Post.query().where('creator_id', '!=', 2).get()
    assert [1, 2, 6, 7] == [x.id for x in posts]

    # Multiple where NOT AND
    posts = await Post.query().where('creator_id', '!=', 2).where('owner_id', '!=', 2).get()
    assert [6, 7] == [x.id for x in posts]

    # Multiple where NOT AND using a LIST
    posts = await Post.query().where([
        ('creator_id', '!=', 2),
        ('owner_id', '!=', 2),
    ]).get()
    assert [6, 7] == [x.id for x in posts]

    # Where NOT OR
    posts = await Post.query().or_where([
        ('creator_id', '!=', 1),
        ('owner_id', '!=', 2)
    ]).get()
    assert [3, 4, 5, 6, 7] == [x.id for x in posts]

    # Where NOT AND with where OR
    posts = await Post.query().where('unique_slug', '!=', 'test-post5').or_where([
        ('creator_id', '!=', 1),
        ('owner_id', '!=', 2)
    ]).get()
    assert [3, 4, 6, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_builder(app1):
    # Single where NOT
    posts = await uvicore.db.query().table('posts').where('creator_id', '!=', 2).get()
    assert [1, 2, 6, 7] == [x.id for x in posts]

    # Multiple where NOT AND
    posts = await uvicore.db.query().table('posts').where('creator_id', '!=', 2).where('owner_id', '!=', 2).get()
    assert [6, 7] == [x.id for x in posts]

    # Multiple where NOT AND using a LIST
    posts = await uvicore.db.query().table('posts').where([
        ('creator_id', '!=', 2),
        ('owner_id', '!=', 2),
    ]).get()
    assert [6, 7] == [x.id for x in posts]

    # Where NOT OR
    posts = await uvicore.db.query().table('posts').or_where([
        ('creator_id', '!=', 1),
        ('owner_id', '!=', 2)
    ]).get()
    assert [3, 4, 5, 6, 7] == [x.id for x in posts]

    # Where NOT AND with where OR
    posts = await uvicore.db.query().table('posts').where('unique_slug', '!=', 'test-post5').or_where([
        ('creator_id', '!=', 1),
        ('owner_id', '!=', 2)
    ]).get()
    assert [3, 4, 6, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_hybrid(app1):
    from app1.database.tables.posts import Posts
    post = Posts.table.c

    # Single NOT where
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id, '!=', 2).get()
    assert [1, 2, 6, 7] == [x.id for x in posts]

    # Single NOT where - binary expression
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id !=  2).get()
    assert [1, 2, 6, 7] == [x.id for x in posts]

    # Multiple where NOT AND
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id, '!=', 2).where(post.owner_id, '!=', 2).get()
    assert [6, 7] == [x.id for x in posts]

    # Multiple where NOT AND - binary expression
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id != 2).where(post.owner_id != 2).get()
    assert [6, 7] == [x.id for x in posts]

    # Multiple where NOT AND using a LIST
    posts = await uvicore.db.query().table(Posts.table).where([
        (post.creator_id, '!=', 2),
        (post.owner_id, '!=', 2),
    ]).get()
    assert [6, 7] == [x.id for x in posts]

    # Multiple where NOT AND using a LIST - binary expression
    posts = await uvicore.db.query().table(Posts.table).where([
        post.creator_id != 2,
        post.owner_id != 2,
    ]).get()
    assert [6, 7] == [x.id for x in posts]

    # Where NOT OR
    posts = await uvicore.db.query().table(Posts.table).or_where([
        (post.creator_id, '!=', 1),
        (post.owner_id, '!=', 2)
    ]).get()
    assert [3, 4, 5, 6, 7] == [x.id for x in posts]

    # Where NOT OR - binary expression
    posts = await uvicore.db.query().table(Posts.table).or_where([
        post.creator_id != 1,
        post.owner_id != 2
    ]).get()
    assert [3, 4, 5, 6, 7] == [x.id for x in posts]

    # Where NOT AND with where OR
    posts = await uvicore.db.query().table(Posts.table).where(post.unique_slug, '!=', 'test-post5').or_where([
        (post.creator_id, '!=', 1),
        (post.owner_id, '!=', 2)
    ]).get()
    assert [3, 4, 6, 7] == [x.id for x in posts]

    # Where NOT AND with where OR - binary expression
    posts = await uvicore.db.query().table(Posts.table).where(post.unique_slug != 'test-post5').or_where([
        post.creator_id != 1,
        post.owner_id != 2
    ]).get()
    assert [3, 4, 6, 7] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_sqlalchemy(app1):
    from app1.database.tables.posts import Posts
    post = Posts.table

    # Single NOT where
    query = post.select().where(post.c.creator_id != 2)
    posts = await uvicore.db.fetchall(query, connection='app1')
    assert [1, 2, 6, 7] == [x.id for x in posts]

    # Multiple where NOT AND
    query = post.select().where(post.c.creator_id != 2).where(post.c.owner_id != 2)
    posts = await uvicore.db.fetchall(query)
    assert [6, 7] == [x.id for x in posts]

    # Multiple where NOT AND using multiple parameters on and_
    query = post.select().where(sa.and_(post.c.creator_id != 2, post.c.owner_id != 2))
    posts = await uvicore.db.fetchall(query)
    assert [6, 7] == [x.id for x in posts]

    # Where NOT OR
    query = post.select().where(sa.or_(post.c.creator_id != 1, post.c.owner_id != 2))
    posts = await uvicore.db.fetchall(query)
    assert [3, 4, 5, 6, 7] == [x.id for x in posts]

    # Where NOT AND with where OR
    query = post.select().where(post.c.unique_slug != 'test-post5').where(sa.or_(post.c.creator_id != 1, post.c.owner_id != 2))
    posts = await uvicore.db.fetchall(query)
    assert [3, 4, 6, 7] == [x.id for x in posts]
