"""
Audit + regression tests for ORM relation MUTATION methods, focused on the
polymorphic relations (MorphOne, MorphMany, MorphToMany) which are the trickiest:

  add() / create()  - insert children (and link, for *ToMany)
  set()             - replace ALL children (delete/unlink then create)
  delete(relation)  - delete children (HasOne, HasMany, MorphOne, MorphMany)
  link() / unlink() - pivot management (BelongsToMany, MorphToMany only)

Each test works on a throwaway post created via the ORM and cleans up after
itself, so the session-shared seed data is untouched.
"""
import pytest
import sqlalchemy as sa
import uvicore


async def _fresh_post(slug):
    from app1.models.post import Post
    for p in await Post.query().where('slug', slug).get():
        await _purge(p)
    return await Post(slug=slug, title='Mut', body='b', creator_id=1, owner_id=2).save()


async def _purge(post):
    from app1.models.comment import Comment
    pid = post.id
    for c in await Comment.query().where('post_id', pid).get():
        await c.delete()
    try: await post.delete('attributes')
    except Exception: pass
    try: await post.delete('image')
    except Exception: pass
    try: await post.unlink('hashtags')
    except Exception: pass
    await post.delete()


async def _attrs(pid):
    from app1.models.attribute import Attribute
    return await Attribute.query().where('attributable_id', pid).where('attributable_type', 'posts').get()


async def _images(pid):
    from app1.models.image import Image
    return await Image.query().where('imageable_id', pid).where('imageable_type', 'posts').get()


async def _hashtag_links(pid):
    t = uvicore.db.table('app1.hashtaggables')
    return await uvicore.db.all(
        sa.select(t).where(t.c.hashtaggable_id == pid).where(t.c.hashtaggable_type == 'posts'),
        connection='app1',
    )


# --------------------------------------------------------------------------
# MorphMany (attributes)
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_morphmany_add_set_delete(app1):
    post = await _fresh_post('zmut-morphmany')
    try:
        await post.add('attributes', [{'key': 'a1', 'value': 'v1'}, {'key': 'a2', 'value': 'v2'}])
        attrs = await _attrs(post.id)
        assert {a.key for a in attrs} == {'a1', 'a2'}
        # The polymorphic type/id were wired correctly on insert
        assert all(a.attributable_type == 'posts' and a.attributable_id == post.id for a in attrs)

        # set() replaces ALL children
        await post.set('attributes', [{'key': 'a3', 'value': 'v3'}])
        attrs = await _attrs(post.id)
        assert {a.key for a in attrs} == {'a3'}

        # delete() removes all children of this relation
        await post.delete('attributes')
        assert len(await _attrs(post.id)) == 0
    finally:
        await _purge(post)


# --------------------------------------------------------------------------
# MorphOne (image)
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_morphone_create_replace_delete(app1):
    post = await _fresh_post('zmut-morphone')
    try:
        await post.create('image', {'filename': 'one.png', 'size': 1})
        images = await _images(post.id)
        assert len(images) == 1 and images[0].filename == 'one.png'
        assert images[0].imageable_type == 'posts' and images[0].imageable_id == post.id

        # Replace via set() (delete then create) - the correct way to swap a MorphOne
        await post.set('image', {'filename': 'two.png', 'size': 2})
        images = await _images(post.id)
        assert len(images) == 1 and images[0].filename == 'two.png'

        await post.delete('image')
        assert len(await _images(post.id)) == 0
    finally:
        await _purge(post)


@pytest.mark.asyncio
async def test_morphone_duplicate_create_violates_uniqueness(app1):
    """A second create() for a MorphOne hits the (type,id) UNIQUE constraint."""
    post = await _fresh_post('zmut-morphone-dup')
    try:
        await post.create('image', {'filename': 'one.png', 'size': 1})
        with pytest.raises(Exception):
            await post.create('image', {'filename': 'two.png', 'size': 2})
        assert len(await _images(post.id)) == 1
    finally:
        await _purge(post)


# --------------------------------------------------------------------------
# MorphToMany (hashtags) - pivot management
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_morphtomany_add_set_unlink(app1):
    from app1.models.hashtag import Hashtag
    hashtags = await Hashtag.query().key_by('name').get()
    important, obsolete = hashtags['important'], hashtags['obsolete']

    post = await _fresh_post('zmut-morphtomany')
    try:
        # add() links existing hashtags (dedup-safe), polymorphic pivot rows created
        await post.add('hashtags', [important, obsolete])
        links = await _hashtag_links(post.id)
        assert len(links) == 2
        assert all(r.hashtaggable_type == 'posts' for r in links)

        # Re-adding the same link is idempotent (no duplicate pivot row)
        await post.add('hashtags', [important])
        assert len(await _hashtag_links(post.id)) == 2

        # set() unlinks all then links the new set
        await post.set('hashtags', [important])
        assert len(await _hashtag_links(post.id)) == 1

        # unlink one specific
        await post.unlink('hashtags', [important])
        assert len(await _hashtag_links(post.id)) == 0

        # unlink-all on a fresh set
        await post.add('hashtags', [important, obsolete])
        await post.unlink('hashtags')
        assert len(await _hashtag_links(post.id)) == 0
    finally:
        await _purge(post)


# --------------------------------------------------------------------------
# Documented limitations (lock in current behavior so changes are intentional)
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_hasmany_add_set_delete(app1):
    """add(), set() (replace all) and delete() all work for a HasMany relation."""
    from app1.models.comment import Comment
    post = await _fresh_post('zmut-hasmany')
    try:
        # add() appends children
        await post.add('comments', [
            {'title': 'c1', 'body': 'b', 'creator_id': 1},
            {'title': 'c2', 'body': 'b', 'creator_id': 1},
        ])
        comments = await Comment.query().where('post_id', post.id).get()
        assert {c.title for c in comments} == {'c1', 'c2'}
        assert all(c.post_id == post.id for c in comments)

        # set() replaces ALL children (delete then create)
        await post.set('comments', [{'title': 'c3', 'body': 'b', 'creator_id': 1}])
        comments = await Comment.query().where('post_id', post.id).get()
        assert {c.title for c in comments} == {'c3'}

        # delete() removes all children of this relation
        await post.delete('comments')
        assert len(await Comment.query().where('post_id', post.id).get()) == 0
    finally:
        await _purge(post)


@pytest.mark.asyncio
async def test_link_unlink_only_for_many_to_many(app1):
    """link()/unlink() reject non-*ToMany relations."""
    post = await _fresh_post('zmut-linkguard')
    try:
        with pytest.raises(Exception):
            await post.link('comments', [{'title': 'x', 'body': 'b', 'creator_id': 1}])
        with pytest.raises(Exception):
            await post.unlink('attributes')
    finally:
        await _purge(post)
