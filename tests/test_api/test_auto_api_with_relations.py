"""
Live HTTP tests for the auto-API POST /{model}/with_relations endpoint.

/with_relations performs a NON-bulk insert that walks nested relations: it
inserts the parent, retrieves its new primary key, and inserts/links the children
wired to that key. This exercises model_router.create_with_relations and
uvicore/orm/model.Model.insert_with_relations across EVERY relation type:

  - HasMany       (post -> comments)
  - BelongsToMany (post -> tags,      via post_tags pivot)
  - MorphOne      (post -> image,     via images polymorphic)
  - MorphMany     (post -> attributes,via attributes polymorphic)
  - MorphToMany   (post -> hashtags,  via hashtaggables polymorphic pivot)
  - BelongsTo     (post -> creator,   child inserted BEFORE parent; also nests
                   the user's own HasOne contact + info)

Payload shapes mirror tests/apps/app1/database/seeders/posts.py. Every test
removes all rows it creates (parent, children, pivot links, and any new
tag/hashtag/user records) so the session-shared in-memory DB stays as seeded.
"""
import pytest
import sqlalchemy as sa
import uvicore

NEW_TAG = 'apitest-rel-newtag'
NEW_HASHTAG = 'apitest-rel-newhashtag'
CREATOR_EMAIL = 'apitest-rel-creator@example.com'


async def _pivot_rows(table_name, **eq):
    """Return rows of a pivot/poly table on the app1 connection filtered by eq columns."""
    tbl = uvicore.db.table('app1.' + table_name)
    query = sa.select(tbl)
    for col, val in eq.items():
        query = query.where(getattr(tbl.c, col) == val)
    return await uvicore.db.all(query, connection='app1')


async def _delete_pivot(table_name, **eq):
    tbl = uvicore.db.table('app1.' + table_name)
    query = tbl.delete()
    for col, val in eq.items():
        query = query.where(getattr(tbl.c, col) == val)
    await uvicore.db.execute(query, connection='app1')


async def _purge_post_and_children(slug):
    """Remove a post and every child/link it could have created."""
    from app1.models.post import Post
    from app1.models.comment import Comment
    from app1.models.image import Image
    from app1.models.attribute import Attribute

    for post in await Post.query().where('slug', slug).get():
        pid = post.id
        for c in await Comment.query().where('post_id', pid).get():
            await c.delete()
        for im in await Image.query().where('imageable_id', pid).where('imageable_type', 'posts').get():
            await im.delete()
        for a in await Attribute.query().where('attributable_id', pid).where('attributable_type', 'posts').get():
            await a.delete()
        await _delete_pivot('post_tags', post_id=pid)
        await _delete_pivot('hashtaggables', hashtaggable_id=pid, hashtaggable_type='posts')
        await post.delete()


async def _purge_new_tag_hashtag():
    from app1.models.tag import Tag
    from app1.models.hashtag import Hashtag
    for t in await Tag.query().where('name', NEW_TAG).get():
        await _delete_pivot('post_tags', tag_id=t.id)
        await t.delete()
    for h in await Hashtag.query().where('name', NEW_HASHTAG).get():
        await _delete_pivot('hashtaggables', hashtag_id=h.id)
        await h.delete()


@pytest.mark.asyncio
async def test_create_with_all_relation_types(apiclient):
    """Insert a Post nesting HasMany, BelongsToMany, MorphOne, MorphMany and MorphToMany."""
    from app1.models.post import Post
    from app1.models.comment import Comment
    from app1.models.image import Image
    from app1.models.attribute import Attribute
    from app1.models.tag import Tag
    from app1.models.hashtag import Hashtag

    SLUG = 'apitest-rel-all'
    await _purge_post_and_children(SLUG)
    await _purge_new_tag_hashtag()

    # Existing seeded records to LINK to (by primary key)
    tags = await Tag.query().key_by('name').get()
    hashtags = await Hashtag.query().key_by('name').get()
    linux, mac = tags['linux'], tags['mac']
    important = hashtags['important']

    new_id = None
    try:
        res = await apiclient.post('/api/posts/with_relations', json={
            'slug': SLUG,
            'title': 'All Relations Post',
            'body': 'parent body',
            'creator_id': 1,
            'owner_id': 2,

            # HasMany
            'comments': [
                {'title': 'C1', 'body': 'cb1', 'creator_id': 1},
                {'title': 'C2', 'body': 'cb2', 'creator_id': 2},
            ],
            # BelongsToMany: link two existing tags (pk set) + create one new tag (no pk)
            'tags': [
                {'id': linux.id, 'name': linux.name, 'creator_id': linux.creator_id},
                {'id': mac.id, 'name': mac.name, 'creator_id': mac.creator_id},
                {'name': NEW_TAG, 'creator_id': 4},
            ],
            # MorphOne
            'image': {'filename': 'apitest-rel.png', 'size': 4242},
            # MorphMany
            'attributes': [
                {'key': 'apitest-a1', 'value': 'v1'},
                {'key': 'apitest-a2', 'value': 'v2'},
            ],
            # MorphToMany: link existing hashtag (pk) + create new one (no pk)
            'hashtags': [
                {'id': important.id, 'name': important.name},
                {'name': NEW_HASHTAG},
            ],
        })
        assert res.status_code == 200, res.text
        created = res.json()
        new_id = created['id']
        assert isinstance(new_id, int)

        # --- HasMany: two comments wired to the new post ---
        comments = await Comment.query().where('post_id', new_id).get()
        assert len(comments) == 2
        assert all(c.post_id == new_id for c in comments)

        # --- MorphOne: one image with the polymorphic type/id set ---
        images = await Image.query().where('imageable_id', new_id).where('imageable_type', 'posts').get()
        assert len(images) == 1
        assert images[0].filename == 'apitest-rel.png'

        # --- MorphMany: two attributes wired polymorphically ---
        attrs = await Attribute.query().where('attributable_id', new_id).where('attributable_type', 'posts').get()
        assert len(attrs) == 2
        assert {a.key for a in attrs} == {'apitest-a1', 'apitest-a2'}

        # --- BelongsToMany: 3 pivot links (2 existing + 1 created), new tag created ---
        tag_links = await _pivot_rows('post_tags', post_id=new_id)
        assert len(tag_links) == 3
        assert len(await Tag.query().where('name', NEW_TAG).get()) == 1

        # --- MorphToMany: 2 polymorphic pivot links, new hashtag created ---
        hashtag_links = await _pivot_rows('hashtaggables', hashtaggable_id=new_id, hashtaggable_type='posts')
        assert len(hashtag_links) == 2
        assert len(await Hashtag.query().where('name', NEW_HASHTAG).get()) == 1

        # --- Read path: ALL relations come back through the API include= ---
        # (HasMany, BelongsToMany, MorphOne, MorphMany, MorphToMany together).
        fetched = await apiclient.get(
            f'/api/posts/{new_id}?include=comments,tags,image,attributes,hashtags'
        )
        assert fetched.status_code == 200, fetched.text
        post = fetched.json()
        assert len(post['comments']) == 2                              # HasMany
        assert len(post['tags']) == 3                                  # BelongsToMany (no cartesian blowup)
        assert post['image'] is not None and post['image']['filename'] == 'apitest-rel.png'  # MorphOne
        assert len(post['attributes']) == 2                            # MorphMany -> dict keyed by 'key'
        assert post['attributes']['apitest-a1'] == 'v1'
        assert len(post['hashtags']) == 2                              # MorphToMany
    finally:
        await _purge_post_and_children(SLUG)
        await _purge_new_tag_hashtag()

    # Fully restored: seed posts intact, no orphaned pivot/poly rows, new records gone
    assert len((await apiclient.get('/api/posts')).json()) == 7
    assert len(await Tag.query().where('name', NEW_TAG).get()) == 0
    assert len(await Hashtag.query().where('name', NEW_HASHTAG).get()) == 0
    if new_id:
        assert len(await _pivot_rows('post_tags', post_id=new_id)) == 0
        assert len(await _pivot_rows('hashtaggables', hashtaggable_id=new_id, hashtaggable_type='posts')) == 0


@pytest.mark.asyncio
async def test_create_with_belongs_to_parent_chain(apiclient):
    """BelongsTo: the nested creator (a User, with its own HasOne contact + info) is
    inserted BEFORE the post, and the post's creator_id is wired to the new user."""
    from app1.models.post import Post
    from uvicore.auth.models.user import User
    from app1.models.contact import Contact
    from app1.models.user_info import UserInfo

    SLUG = 'apitest-rel-belongsto'

    async def purge():
        for post in await Post.query().where('slug', SLUG).get():
            await post.delete()
        for user in await User.query().where('email', CREATOR_EMAIL).get():
            for ct in await Contact.query().where('user_id', user.id).get():
                await ct.delete()
            for nfo in await UserInfo.query().where('user_id', user.id).get():
                await nfo.delete()
            await user.delete()

    await purge()
    try:
        res = await apiclient.post('/api/posts/with_relations', json={
            'slug': SLUG,
            'title': 'BelongsTo Post',
            'body': 'body',
            'owner_id': 3,
            # BelongsTo creator inserted first; it nests its own HasOne contact + info
            'creator': {
                'username': CREATOR_EMAIL,
                'email': CREATOR_EMAIL,
                'first_name': 'Rel',
                'last_name': 'Creator',
                'creator_id': 1,
                'password': 'techie',
                'contact': {
                    'name': 'Rel Creator',
                    'title': 'Tester',
                    'address': '1 Test Way',
                    'phone': '555-555-5555',
                },
                'info': {'extra1': 'rel creator extra'},
            },
        })
        assert res.status_code == 200, res.text
        post_id = res.json()['id']

        # The creator user was created child-first
        users = await User.query().where('email', CREATOR_EMAIL).get()
        assert len(users) == 1
        creator = users[0]

        # The post's creator_id (the BelongsTo foreign key) points at the new user
        post = await Post.query().find(post_id)
        assert post.creator_id == creator.id

        # The user's own nested HasOne children were created and wired to the user
        contacts = await Contact.query().where('user_id', creator.id).get()
        infos = await UserInfo.query().where('user_id', creator.id).get()
        assert len(contacts) == 1 and contacts[0].name == 'Rel Creator'
        assert len(infos) == 1 and infos[0].extra1 == 'rel creator extra'

        # Read path: include the BelongsTo chain through the API
        fetched = await apiclient.get(f'/api/posts/{post_id}?include=creator.contact')
        assert fetched.status_code == 200, fetched.text
        assert fetched.json()['creator']['email'] == CREATOR_EMAIL
    finally:
        await purge()

    assert len((await apiclient.get('/api/posts')).json()) == 7
    assert len(await User.query().where('email', CREATOR_EMAIL).get()) == 0
