import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

@pytest.mark.asyncio
async def test_join(app1):
    import sqlalchemy as sa

    query = (uvicore.db.query('app1')
        .table('posts')

        # Join users from posts.creator_id (many-to-one)
        .join('auth.users', 'posts.creator_id', 'auth.users.id', alias='creator')

        # Join in contacts for each user (one-to-one)
        .join('contacts', 'auth.users.id', 'contacts.user_id', alias='creator__contact')

        # Order for consistent assertions
        .order_by('posts.id', 'DESC')
    )
    results = await query.get()
    print(query.sql())
    dump(results)

    # These are the unique keys
    # Notice no name collisions, all with __ for nested relations, ie: creator__contact__address
    # sqlalchemy.sql.elements.quoted_name('id'),
    # sqlalchemy.sql.elements.quoted_name('unique_slug'),
    # sqlalchemy.sql.elements.quoted_name('title'),
    # sqlalchemy.sql.elements.quoted_name('body'),
    # sqlalchemy.sql.elements.quoted_name('other'),
    # sqlalchemy.sql.elements.quoted_name('creator_id'),
    # sqlalchemy.sql.elements.quoted_name('owner_id'),
    # sqlalchemy.sql.elements.quoted_name('creator__id'),
    # sqlalchemy.sql.elements.quoted_name('creator__uuid'),
    # sqlalchemy.sql.elements.quoted_name('creator__username'),
    # sqlalchemy.sql.elements.quoted_name('creator__email'),
    # sqlalchemy.sql.elements.quoted_name('creator__first_name'),
    # sqlalchemy.sql.elements.quoted_name('creator__last_name'),
    # sqlalchemy.sql.elements.quoted_name('creator__title'),
    # sqlalchemy.sql.elements.quoted_name('creator__avatar_url'),
    # sqlalchemy.sql.elements.quoted_name('creator__password'),
    # sqlalchemy.sql.elements.quoted_name('creator__disabled'),
    # sqlalchemy.sql.elements.quoted_name('creator__creator_id'),
    # sqlalchemy.sql.elements.quoted_name('creator__created_at'),
    # sqlalchemy.sql.elements.quoted_name('creator__updated_at'),
    # sqlalchemy.sql.elements.quoted_name('creator__login_at'),
    # sqlalchemy.sql.elements.quoted_name('creator__app1_extra'),
    # sqlalchemy.sql.elements.quoted_name('creator__contact__id'),
    # sqlalchemy.sql.elements.quoted_name('creator__contact__name'),
    # sqlalchemy.sql.elements.quoted_name('creator__contact__title'),
    # sqlalchemy.sql.elements.quoted_name('creator__contact__address'),
    # sqlalchemy.sql.elements.quoted_name('creator__contact__phone'),
    # sqlalchemy.sql.elements.quoted_name('creator__contact__user_id')
    dump(results[0].keys())

    # Access first level deep
    assert [
        'test-post7',
        'test-post6',
        'test-post5',
        'test-post4',
        'test-post3',
        'test-post2',
        'test-post1',
    ] == [x.unique_slug for x in results]

    # Access second level deep with creator__email
    assert [
        'user1@example.com',
        'user2@example.com',
        'administrator@example.com',
        'administrator@example.com',
        'administrator@example.com',
        'anonymous@example.com',
        'anonymous@example.com',
    ] == [x.creator__email for x in results]

    # Access third level deep with creator__contact__address
    assert [
        '333 User Dr.',
        '444 User Dr.',
        '777 Heaven Ln',
        '777 Heaven Ln',
        '777 Heaven Ln',
        '999 Anonymous Dr.',
        '999 Anonymous Dr.',
    ] == [x.creator__contact__address for x in results]


@pytest.mark.asyncio
async def test_join_wheredot(app1):
    import sqlalchemy as sa

    query = (uvicore.db.query('app1')
        .table('posts')

        # Join users from posts.creator_id (many-to-one)
        .join('auth.users', 'posts.creator_id', 'auth.users.id', alias='creator')

        # Where using nested dod notation
        .where('creator.email', 'administrator@example.com')

        # Order for consistent assertions
        .order_by('posts.id', 'ASC')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())  # Notice no name collisions
    assert [
        'test-post3',
        'test-post4',
        'test-post5',
    ] == [x.unique_slug for x in results]
    assert [
        'administrator@example.com',
        'administrator@example.com',
        'administrator@example.com',
    ] == [x.creator__email for x in results]



@pytest.mark.asyncio
async def test_join_whereunderscore(app1):
    import sqlalchemy as sa

    query = (uvicore.db.query('app1')
        .table('posts')

        # Join users from posts.creator_id (many-to-one)
        .join('auth.users', 'posts.creator_id', 'auth.users.id', alias='creator')

        # Where using nested dod notation
        .where('creator__email', 'administrator@example.com')

        # Order for consistent assertions
        .order_by('posts.id', 'ASC')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())  # Notice no name collisions
    assert [
        'test-post3',
        'test-post4',
        'test-post5',
    ] == [x.unique_slug for x in results]
    assert [
        'administrator@example.com',
        'administrator@example.com',
        'administrator@example.com',
    ] == [x.creator__email for x in results]



@pytest.mark.asyncio
async def test_join_orwhere(app1):
    import sqlalchemy as sa

    query = (uvicore.db.query('app1')
        .table('posts')

        # Join users from posts.creator_id (many-to-one)
        .join('auth.users', 'posts.creator_id', 'auth.users.id', alias='creator')

        # Or where using both dot and __ notation
        .or_where([
            ('creator.email', 'administrator@example.com'),
            ('creator__email', 'user1@example.com')
        ])

        # Order for consistent assertions
        .order_by('posts.id', 'ASC')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())  # Notice no name collisions
    assert [
        'test-post3',
        'test-post4',
        'test-post5',
        'test-post7',
    ] == [x.unique_slug for x in results]
    assert [
        'administrator@example.com',
        'administrator@example.com',
        'administrator@example.com',
        'user1@example.com',
    ] == [x.creator__email for x in results]


@pytest.mark.asyncio
async def test_join_order_by(app1):
    query = (uvicore.db.query('app1')
        .table('posts')

        # Join users from posts.creator_id (many-to-one)
        .join('auth.users', 'posts.creator_id', 'auth.users.id', alias='creator')

        # Order by using nested dot notation, notice order on CHILDREN, not post
        .order_by('creator.email', 'DESC')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert [
        'test-post6',
        'test-post7',
        'test-post1',
        'test-post2',
        'test-post3',
        'test-post4',
        'test-post5',
    ] == [x.unique_slug for x in results]
    assert [
        'user2@example.com',
        'user1@example.com',
        'anonymous@example.com',
        'anonymous@example.com',
        'administrator@example.com',
        'administrator@example.com',
        'administrator@example.com',
    ] == [x.creator__email for x in results]


@pytest.mark.asyncio
async def test_join_group_by(app1):
    import sqlalchemy as sa
    from app1.database.tables.posts import Posts

    # In order to use any raw SQLAlchemy function, you must get the actual table
    # This is a hybrid because of the count(), but we want to test a STRING order_by
    posts = Posts.table.c

    query = (uvicore.db.query('app1')
        .table('posts')

        # Join users from posts.creator_id (many-to-one)
        .join('auth.users', 'posts.creator_id', 'auth.users.id', alias='creator')

        # Select nested field and count()
        # Testing both relation dot and __ notation
        .select('creator.email', 'creator__first_name', sa.func.count(posts.id))

        # Group by nested field
        .group_by('creator.email', 'creator__first_name')

        # Order for consistent results
        .order_by('creator.email')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())
    assert [
        ('administrator@example.com', 'Admin', 3),
        ('anonymous@example.com', 'Anonymous', 2),
        ('user1@example.com', 'User', 1),
        ('user2@example.com', 'User', 1)
    ] == results
