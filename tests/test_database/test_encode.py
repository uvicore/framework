import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_select_all(app1):
    from app1.database.tables.posts import Posts

    query = Posts.table.select()
    results = await uvicore.db.fetchall(query, connection='app1')
    dump(results)
    assert [
        'test-post1',
        'test-post2',
        'test-post3',
        'test-post4',
        'test-post5',
        'test-post6',
        'test-post7'
    ] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_join1(app1):
    from app1.database.tables.contacts import Contacts
    from app1.database.tables.users import Users

    # Implied join on columns works only if there is one foreign key.
    # Won't work on posts because posts has both a creator_id and owner_id
    # posts = Posts.table
    # users = Users.table
    # query = (
    #     sa.select([posts, users])
    #     .select_from(posts.join(users))
    #     .where(users.c.email == 'manager1@example.com')
    #     .where(posts.c.id == 3)
    # )
    # results = await uvicore.db.fetchall(query, connection='app1')
    # assert ['manager1@example.com'] == [x.email for x in results]

    contacts = Contacts.table
    users = Users.table
    query = (
        sa.select([contacts, users])
        .select_from(contacts.join(users))
        .where(users.c.email == 'manager1@example.com')
    )
    results = await uvicore.db.fetchall(query, connection='app1')
    dump(results)
    assert ['manager1@example.com'] == [x.email for x in results]


@pytest.mark.asyncio
async def test_join2(app1):
    from sqlalchemy import select
    from app1.database.tables.posts import Posts
    from app1.database.tables.users import Users
    from app1.database.tables.contacts import Contacts
    from app1.database.tables.comments import Comments

    # This looks close to my own Db Query Builder but you have to manually .fetchall()
    # and the returned RowProxy has column name collisions.  You would have to select
    # each column and add a .label() to avoid collisions.  So my query builder is still
    # a lot simpler and a bit better looking.
    posts, users, contacts, comments = Posts.table, Users.table, Contacts.table, Comments.table
    query = (
        select([posts, users, contacts, comments])
        .select_from(posts
            .join(users, posts.c.creator_id == users.c.id)
            .join(contacts, users.c.id == contacts.c.user_id)
            .join(comments, posts.c.id == comments.c.post_id)
        )
    )
    results = await uvicore.db.fetchall(query, connection='app1')
    dump(results)
    dump(results[0].keys())  # Notice name collissions
    assert [
        'test-post1',
        'test-post1',
        'test-post3',
        'test-post3',
        'test-post3',
    ] == [x.unique_slug for x in results]


@pytest.mark.asyncio
async def test_group_by(app1):
    from app1.database.tables.posts import Posts

    posts = Posts.table
    query = (
        sa.select([
            posts.c.creator_id,
            sa.func.count(posts.c.title)
        ])
        .group_by(posts.c.creator_id)
    )

    results = await uvicore.db.fetchall(query, connection='app1')
    dump(results)

    assert results == [
        (1, 2),
        (2, 3),
        (5, 2)
    ]
