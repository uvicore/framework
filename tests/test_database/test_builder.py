import pytest
import uvicore
from uvicore.support.dumper import dump


# Builder is a pure STRING based builder.  Don't mix in any SQLAlchemy columns
# of functions.  I test all those in test_hybrid.py

@pytest.mark.asyncio
async def test_select_all(app1):
    posts = (await uvicore.db.query()
        .table('posts')
        .get()
    )
    dump(posts)
    assert [
        'test-post1',
        'test-post2',
        'test-post3',
        'test-post4',
        'test-post5',
        'test-post6',
        'test-post7'
    ] == [x.unique_slug for x in posts]


@pytest.mark.asyncio
async def test_select_one(app1):
    post = (await uvicore.db.query('app1')
        .table('posts')
        .find(2)
    )
    assert post.unique_slug == 'test-post2'


@pytest.mark.asyncio
async def test_where_in(app1):
    query = (uvicore.db.query('app1')
        .table('posts')
        .where('unique_slug', 'in', [
            'test-post1',
            'test-post2',
        ])
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert ['test-post1', 'test-post2'] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_where_not_in(app1):
    query = (uvicore.db.query('app1')
        .table('posts')
        .where('unique_slug', '!in', [
            'test-post1',
            'test-post2',
            'test-post5',
        ])
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert ['test-post3', 'test-post4', 'test-post6', 'test-post7'] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_where_like(app1):
    query = (uvicore.db.query('app1')
        .table('posts')
        .where('other', 'like', 'other stuff%')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert ['test-post1', 'test-post3', 'test-post6'] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_where_not_like(app1):
    query = (uvicore.db.query('app1')
        .table('posts')
        .where('other', '!like', '%1')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert ['test-post3', 'test-post6'] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_where_null(app1):
    query = (uvicore.db.query('app1')
        .table('posts')
        .where('other', 'null')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert ['test-post2', 'test-post4', 'test-post5', 'test-post7'] == [x.unique_slug for x in results]
    #assert 1 == 2


@pytest.mark.asyncio
async def test_where_not_null(app1):
    query = (uvicore.db.query('app1')
        .table('posts')
        .where('other', '!=', 'null')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert ['test-post1', 'test-post3', 'test-post6'] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_or_where(app1):
    query = (uvicore.db.query('app1')
        .table('posts')
        .or_where([
            ('id', '=', 1),
            ('id', 2)
        ])
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert ['test-post1', 'test-post2'] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_join(app1):
    import sqlalchemy as sa

    query = (uvicore.db.query('app1')
        .table('posts')

        # Test with table as real SQLAlchemy Table and columns as strings
        .join('auth.users', 'posts.creator_id', 'auth.users.id', alias='creator')

        # Test with string table and columns as real SQLAlchemy
        .join('contacts', 'auth.users.id', 'contacts.user_id', alias='creator__contact')

        # Test with SQLAlchemy Binary Expression
        .join('comments', 'posts.id', 'comments.post_id')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())  # Notice no name collisions
    assert [
        'test-post1',
        'test-post1',
        'test-post3',
        'test-post3',
        'test-post3',
    ] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_outerjoin(app1):
    import sqlalchemy as sa

    query = (uvicore.db.query('app1')
        .table('posts')

        # Test with table as real SQLAlchemy Table and columns as strings
        .join('auth.users', 'posts.creator_id', 'auth.users.id', alias='creator')

        # Test with string table and columns as real SQLAlchemy
        .join('contacts', 'auth.users.id', 'contacts.user_id', alias='creator__contact')

        # Test with SQLAlchemy Binary Expression
        .outer_join('comments', 'posts.id', 'comments.post_id')

        # Where shows posts WITHOUT a comment
        .where('comments.id', None)

        # And wheres from a JOIN alias called 'creator'
        .where('creator.email', 'manager1@example.com')
        #.where('creator__contact.phone', '111-111-1111')  # This also works with a bigger alias

        # This also works, but only because we joined auth_users once
        # If we joined it twice on say owner_id, this would mess up
        #.where('auth.users.email', 'manager1@example.com')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())  # Notice no name collisions
    assert [
        'test-post4',
        'test-post5',
    ] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_order_by(app1):
    query = (uvicore.db.query('app1')
        .table('posts')
        .order_by('id', 'DESC')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert [
        'test-post7',
        'test-post6',
        'test-post5',
        'test-post4',
        'test-post3',
        'test-post2',
        'test-post1',
    ] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_group_by(app1):
    import sqlalchemy as sa
    from app1.database.tables.posts import Posts

    # In order to use any raw SQLAlchemy function, you must get the actual table
    # This is a hybrid because of the count(), but we want to test a STRING order_by
    posts = Posts.table.c

    query = (uvicore.db.query('app1')
        .table('posts')
        .select('creator_id', sa.func.count(posts.id))
        .group_by('creator_id')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert [(1, 2), (2, 3), (5, 2)] == results
