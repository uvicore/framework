import pytest
import sqlalchemy as sa

import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_orm(app1):
    from app1.models.post import Post

    # Single where
    posts = await Post.query().where('creator_id', 2).get()
    assert [3, 4, 5] == [x.id for x in posts]

    # Multiple where AND
    posts = await Post.query().where('creator_id', '=', 2).where('owner_id', 1).get()
    assert [3, 4] == [x.id for x in posts]

    # Multiple where AND using a LIST
    posts = await Post.query().where([
        ('creator_id', '=', 2),
        ('owner_id', 1)
    ]).get()
    assert [3, 4] == [x.id for x in posts]

    # Where OR
    posts = await Post.query().or_where([
        ('slug', 'test-post3'),
        ('slug', '=', 'test-post4'),
    ]).get()
    assert [3, 4] == [x.id for x in posts]

    # Where AND with where OR
    posts = await Post.query().where('creator_id', '=', 2).or_where([
        ('slug', 'test-post3'),
        ('slug', '=', 'test-post4'),
    ]).get()
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_builder(app1):
    # Single where
    query = uvicore.db.query('app1').table('posts').where('creator_id', 2)
    posts = await query.get()
    #print(query.sql());dump(posts); dump(posts[0].keys())
    assert [3, 4, 5] == [x.id for x in posts]

    # Multiple where AND
    posts = await uvicore.db.query().table('posts').where('creator_id', '=', 2).where('owner_id', 1).get()
    #print(query.sql());dump(posts); dump(posts[0].keys())
    assert [3, 4] == [x.id for x in posts]

    # Multiple where AND using a LIST
    posts = await uvicore.db.query().table('posts').where([
        ('creator_id', '=', 2),
        ('owner_id', 1),
    ]).get()
    assert [3, 4] == [x.id for x in posts]

    # Where OR
    posts = await uvicore.db.query().table('posts').or_where([
        ('unique_slug', 'test-post3'),
        ('unique_slug', '=', 'test-post4'),
    ]).get()
    assert [3, 4] == [x.id for x in posts]

    # Where AND with where OR
    posts = await uvicore.db.query().table('posts').where('creator_id', '=', 2).or_where([
        ('unique_slug', 'test-post3'),
        ('unique_slug', '=', 'test-post4'),
    ]).get()
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_hybrid(app1):
    from app1.database.tables.posts import Posts
    post = Posts.table.c

    # Single where
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id, 2).get()
    assert [3, 4, 5] == [x.id for x in posts]

    # Single where - binary expression
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id == 2).get()
    assert [3, 4, 5] == [x.id for x in posts]

    # Multiple where AND
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id, '=', 2).where(post.owner_id, 1).get()
    assert [3, 4] == [x.id for x in posts]

    # Multiple where AND - binary expression
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id == 2).where(post.owner_id == 1).get()
    assert [3, 4] == [x.id for x in posts]

    # Multiple where AND using a LIST
    posts = await uvicore.db.query().table(Posts.table).where([
        (post.creator_id, '=', 2),
        (post.owner_id, 1),
    ]).get()
    assert [3, 4] == [x.id for x in posts]

    # Multiple where AND using a LIST - binary expression
    posts = await uvicore.db.query().table(Posts.table).where([
        post.creator_id == 2,
        post.owner_id == 1
    ]).get()
    assert [3, 4] == [x.id for x in posts]

    # Where OR
    posts = await uvicore.db.query().table(Posts.table).or_where([
        (post.unique_slug, 'test-post3'),
        (post.unique_slug, '=', 'test-post4'),
    ]).get()
    assert [3, 4] == [x.id for x in posts]

    # Where OR - binary expression
    posts = await uvicore.db.query().table(Posts.table).or_where([
        post.unique_slug == 'test-post3',
        post.unique_slug == 'test-post4',
    ]).get()
    assert [3, 4] == [x.id for x in posts]

    # Where AND with where OR
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id, '=', 2).or_where([
        (post.unique_slug, 'test-post3'),
        (post.unique_slug, '=', 'test-post4'),
    ]).get()
    assert [3, 4] == [x.id for x in posts]

    # Where AND with where OR - binary expression
    posts = await uvicore.db.query().table(Posts.table).where(post.creator_id == 2).or_where([
        post.unique_slug == 'test-post3',
        post.unique_slug == 'test-post4',
    ]).get()
    assert [3, 4] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_sqlalchemy(app1):
    from app1.database.tables.posts import Posts
    post = Posts.table

    # Single where
    query = post.select().where(post.c.creator_id == 2)
    posts = await uvicore.db.fetchall(query, connection='app1')
    assert [3, 4, 5] == [x.id for x in posts]

    # Multiple where AND
    query = post.select().where(post.c.creator_id == 2).where(post.c.owner_id == 1)
    posts = await uvicore.db.fetchall(query)
    assert [3, 4] == [x.id for x in posts]

    # Multiple where AND using multiple parameters on and_
    query = post.select().where(sa.and_(post.c.creator_id == 2, post.c.owner_id == 1))
    posts = await uvicore.db.fetchall(query)
    assert [3, 4] == [x.id for x in posts]

    # Where OR
    query = post.select().where(sa.or_(post.c.unique_slug == 'test-post3', post.c.unique_slug == 'test-post4'))
    posts = await uvicore.db.fetchall(query)
    assert [3, 4] == [x.id for x in posts]

    # Where AND with where OR
    query = post.select().where(post.c.creator_id == 2).where(sa.or_(post.c.unique_slug == 'test-post3', post.c.unique_slug == 'test-post4'))
    posts = await uvicore.db.fetchall(query)
    assert [3, 4] == [x.id for x in posts]
