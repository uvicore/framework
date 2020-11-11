import pytest
from starlette.testclient import TestClient

import uvicore
from uvicore.support.dumper import dump

# Hybrid is where I use my Database Query Builder but with SQLAlchemy
# table.c columns operations, aggregate functions and Binary Expressions

@pytest.mark.asyncio
async def test_select_count(app1):
    import sqlalchemy as sa
    from app1.database.tables.posts import Posts

    # You can use any SQLAlchemy Core Generic Function (sa.func.xyz) in a select statement
    # as long as you get the actual Table.c (Posts.table.c)
    posts = Posts.table.c
    query = (uvicore.db.query('app1')
        .table(Posts.table)
        .select(posts.creator_id, sa.func.count(posts.id))  # Or can leave blank for *
        #.select(posts.creator_id, sa.func.count(posts.id).label('cnt'))  # Can label it too, defaults to count_1
        .group_by(posts.creator_id)
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert [(1, 2), (2, 3), (5, 2)] == results


@pytest.mark.asyncio
async def test_select_max(app1):
    import sqlalchemy as sa
    from app1.database.tables.posts import Posts

    posts = Posts.table.c
    query = (uvicore.db.query('app1')
        .table(Posts.table)
        .select(sa.func.max(posts.id))
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert [(7,)] == results


@pytest.mark.asyncio
async def test_selects(app1):
    import sqlalchemy as sa
    from app1.database.tables.posts import Posts
    from app1.database.tables.users import Users
    from app1.database.tables.contacts import Contacts

    posts, users, contacts = Posts.table.c, Users.table.c, Contacts.table.c
    query = (uvicore.db.query('app1')
        .table(Posts.table)

        .select(posts.id, posts.unique_slug, users.email, 'auth.users.app1_extra')

        # Test with table as real SQLAlchemy Table and columns as strings
        .join(Users.table, 'posts.creator_id', 'auth.users.id')

        # Test with string table and columns as real SQLAlchemy
        .join('contacts', users.id, contacts.user_id)
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())  # Notice no name collisions
    assert [
        (1, 'test-post1', 'administrator@example.com', 'hi'),
        (2, 'test-post2', 'administrator@example.com', 'hi'),
        (3, 'test-post3', 'manager1@example.com', None),
        (4, 'test-post4', 'manager1@example.com', None),
        (5, 'test-post5', 'manager1@example.com', None),
        (6, 'test-post6', 'user2@example.com', None),
        (7, 'test-post7', 'user2@example.com', None)
    ] == results


@pytest.mark.asyncio
async def test_where_column(app1):
    from app1.database.tables.posts import Posts

    # Test where as SQLAlchemy Column name but still parameter based
    posts = Posts.table.c
    query = (uvicore.db.query('app1')
        .table(Posts.table)
        .where(posts.creator_id, '=', 2)
        .where(posts.unique_slug, 'test-post4')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert [(4, 'test-post4', 'Test Post4', None, 2, 1)] == results


@pytest.mark.asyncio
async def test_where_column_list(app1):
    from app1.database.tables.posts import Posts

    # Test where as SQLAlchemy Column name but still parameter based
    posts = Posts.table.c
    query = (uvicore.db.query('app1')
        .table(Posts.table)
        .where([
            (posts.creator_id, '=', 2),
            (posts.unique_slug, 'test-post4'),
        ])
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert [(4, 'test-post4', 'Test Post4', None, 2, 1)] == results


@pytest.mark.asyncio
async def test_where_expression(app1):
    from app1.database.tables.posts import Posts

    # Test where as SQLAlchemy Binary Expression
    posts = Posts.table.c
    query = (uvicore.db.query('app1')
        .table(Posts.table)
        .where(posts.creator_id == 2)
        .where(posts.unique_slug == 'test-post4')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert [(4, 'test-post4', 'Test Post4', None, 2, 1)] == results


@pytest.mark.asyncio
async def test_where_expression_list(app1):
    from app1.database.tables.posts import Posts

    # Test where as SQLAlchemy Binary Expression
    posts = Posts.table.c
    query = (uvicore.db.query('app1')
        .table(Posts.table)
        .where([
            posts.creator_id == 2,
            posts.unique_slug == 'test-post4',
        ])
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert [(4, 'test-post4', 'Test Post4', None, 2, 1)] == results


@pytest.mark.asyncio
async def test_or_where_column(app1):
    from app1.database.tables.posts import Posts

    # Test OR where as SQLAlchemy Column name but still parameter based
    posts = Posts.table.c
    query = (uvicore.db.query('app1')
        .table(Posts.table)
        .or_where([
            (posts.creator_id, '=', 2),
            (posts.unique_slug, 'test-post1'),
        ])
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert ['test-post1', 'test-post3', 'test-post4', 'test-post5'] == [x.unique_slug for x in results]
    #assert 1 == 2


@pytest.mark.asyncio
async def test_or_where_expression(app1):
    from app1.database.tables.posts import Posts

    # Test OR where as SQLAlchemy Binary Expression
    posts = Posts.table.c
    query = (uvicore.db.query('app1')
        .table(Posts.table)
        .or_where([
            posts.creator_id == 2,
            posts.unique_slug == 'test-post1',
        ])
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert ['test-post1', 'test-post3', 'test-post4', 'test-post5'] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_join(app1):
    import sqlalchemy as sa
    from app1.database.tables.posts import Posts
    from app1.database.tables.users import Users
    from app1.database.tables.contacts import Contacts
    from app1.database.tables.comments import Comments

    # Compare this with test_encode.py test_join2() to see what it looks like as a raw
    # SQLAlchemy core query.  Mine is a bit simpler and has more benifits like auto select labels()
    # to avoid RowProxy name collisions.
    posts, users, contacts, comments = Posts.table.c, Users.table.c, Contacts.table.c, Comments.table.c
    query = (uvicore.db.query('app1')
        .table(Posts.table)

        # Test with table as real SQLAlchemy Table and columns as strings
        .join(Users.table, 'posts.creator_id', 'auth.users.id', alias='creator')

        # Test with string table and columns as real SQLAlchemy
        .join('contacts', users.id, contacts.user_id, alias='creator__contact')

        # Test with SQLAlchemy Binary Expression
        .join(Comments.table, posts.id == comments.post_id)
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
async def test_order_by(app1):
    import sqlalchemy as sa
    from app1.database.tables.posts import Posts

    posts = Posts.table.c
    query = (uvicore.db.query('app1')
        .table('posts')  # Notice can use string 'posts' or Posts.table (hybrid)
        .order_by(sa.desc(posts.id))  # Cannot use string 'posts.id', has to be from Posts table.c
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    assert [
        'test-post7',
        'test-post6',
        'test-post5',
        'test-post4',
        'test-post3',
        'test-post2',
        'test-post1',
    ] == [x.unique_slug for x in results]
