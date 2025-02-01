import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Hybrid

@pytest.mark.asyncio
async def test_join(app1):
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

        # Order for consistent assertions
        .order_by(posts.id, 'ASC')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0]._mapping.keys())  # Notice no name collisions
    assert [
        (1, 'test-post1', 'anonymous@example.com', None),
        (2, 'test-post2', 'anonymous@example.com', None),
        (3, 'test-post3', 'administrator@example.com', 'hi'),
        (4, 'test-post4', 'administrator@example.com', 'hi'),
        (5, 'test-post5', 'administrator@example.com', 'hi'),
        (6, 'test-post6', 'user2@example.com', None),
        (7, 'test-post7', 'user1@example.com', None)
    ] == results


@pytest.mark.asyncio
async def test_join_one_to_many(app1):
    import sqlalchemy as sa
    from app1.database.tables.posts import Posts
    from app1.database.tables.users import Users
    from app1.database.tables.contacts import Contacts
    from app1.database.tables.comments import Comments

    # Compare this with test_db_sa/test_join/test_join_one_to_many to see what it looks like as a raw
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

        # Order for consistent assertions, using SA column and String order
        .order_by(posts.id, 'DESC')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0]._mapping.keys())  # Notice no name collisions
    assert [
        'test-post3',
        'test-post3',
        'test-post3',
        'test-post1',
        'test-post1',
    ] == [x.unique_slug for x in results]
