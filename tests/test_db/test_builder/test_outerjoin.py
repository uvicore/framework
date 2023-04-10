import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump

# DB Builder

@pytest.mark.asyncio
async def test_outerjoin(app1):
    import sqlalchemy as sa

    query = (uvicore.db.query('app1')
        .table('posts')

        # Join users from posts.creator_id (many-to-one)
        .join('auth.users', 'posts.creator_id', 'auth.users.id', alias='creator')

        # Join in contacts for each user (one-to-one)
        .join('contacts', 'auth.users.id', 'contacts.user_id', alias='creator__contact')

        # Outer join post comments
        .outer_join('comments', 'posts.id', 'comments.post_id') # default alias is comments__

        # Order for consistent assertions
        .order_by('posts.id', 'DESC')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())  # Notice no name collisions
    assert [
        'test-post7',
        'test-post6',
        'test-post5',
        'test-post4',
        'test-post3', # post 3 has 3 comments
        'test-post3',
        'test-post3',
        'test-post2',
        'test-post1', # post 1 has 2 comments
        'test-post1',
    ] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_outerjoin_where_no_match(app1):
    import sqlalchemy as sa

    query = (uvicore.db.query('app1')
        .table('posts')

        # Join users from posts.creator_id (many-to-one)
        .join('auth.users', 'posts.creator_id', 'auth.users.id', alias='creator')

        # Join in contacts for each user (one-to-one)
        .join('contacts', 'auth.users.id', 'contacts.user_id', alias='creator__contact')

        # Outer join post comments
        .outer_join('comments', 'posts.id', 'comments.post_id') # default alias is comments__

        # Where shows posts WITHOUT a comment
        .where('comments.id', None)

        # Order for consistent assertions
        .order_by('posts.id', 'DESC')

        # And wheres from a JOIN alias called 'creator'
        #.where('creator.email', 'administrator@example.com')
        #.where('creator__email', 'user1@example.com')  # This also works with a bigger alias

        # This also works, but only because we joined auth_users once
        # If we joined it twice on say owner_id, this would mess up, so don't use this
        #.where('auth.users.email', 'user1@example.com')
    )
    results = await query.get()
    print(query.sql())
    dump(results)
    dump(results[0].keys())  # Notice no name collisions
    # These posts have NO comments, only post 1 and 3 have comments
    assert [
        'test-post7',
        'test-post6',
        'test-post5',
        'test-post4',
        'test-post2',
    ] == [x.unique_slug for x in results]

