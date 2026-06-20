"""
Live HTTP tests for the auto-API write endpoints (POST / PATCH / PUT / DELETE).

Records are created and always removed within each test so the session-shared
in-memory database stays as seeded. The PATCH/PUT-with-relations tests document
that those endpoints update SCALAR columns only and ignore nested relation keys
(by design - relations are managed via /with_relations and the relation methods).
"""
import pytest


@pytest.mark.asyncio
async def test_update_replace_delete_roundtrip(apiclient):
    """PATCH (partial), PUT (full replace) and DELETE via the auto API."""
    from app1.models.post import Post

    # Arrange: create a throwaway record directly via the ORM
    post = await Post(
        slug='apitest-write',
        title='Original Title',
        body='Original body.',
        creator_id=1,
        owner_id=2,
    ).save()
    new_id = post.id

    try:
        # Sanity: readable through the API
        res = await apiclient.get(f'/api/posts/{new_id}')
        assert res.status_code == 200, res.text
        assert res.json()['title'] == 'Original Title'

        # PATCH (partial update) — only 'title' changes, 'slug' untouched
        res = await apiclient.patch(f'/api/posts/{new_id}', json={'title': 'Patched Title'})
        assert res.status_code == 200, res.text
        body = await apiclient.get(f'/api/posts/{new_id}')
        assert body.json()['title'] == 'Patched Title'
        assert body.json()['slug'] == 'apitest-write'

        # PUT (full replace) — requires a complete object
        res = await apiclient.put(f'/api/posts/{new_id}', json={
            'slug': 'apitest-write',
            'title': 'Replaced Title',
            'body': 'Replaced body.',
            'creator_id': 1,
            'owner_id': 2,
        })
        assert res.status_code == 200, res.text
        body = await apiclient.get(f'/api/posts/{new_id}')
        assert body.json()['title'] == 'Replaced Title'
        assert body.json()['body'] == 'Replaced body.'

        # DELETE
        res = await apiclient.delete(f'/api/posts/{new_id}')
        assert res.status_code == 200, res.text

        # Gone
        res = await apiclient.get(f'/api/posts/{new_id}')
        assert res.status_code == 404, res.text
    finally:
        # Guarantee cleanup even if an assertion above failed mid-roundtrip
        leftover = await Post.query().find(new_id)
        if leftover:
            await leftover.delete()

    # Seed count restored
    res = await apiclient.get('/api/posts')
    assert len(res.json()) == 7


@pytest.mark.asyncio
async def test_delete_missing_returns_404(apiclient):
    """DELETE of a non-existent id returns 404, not 500."""
    res = await apiclient.delete('/api/posts/99999')
    assert res.status_code == 404, res.text


@pytest.mark.asyncio
async def test_create_single_via_post(apiclient):
    """POST a single new model and get it back with its new primary key populated.

    Regression test for the model_router.create bug where Model.insert() returns a
    SQLAlchemy CursorResult (not the pk); the endpoint stored the CursorResult into
    the model's id, which then failed response_model validation (500). The fix
    extracts result.inserted_primary_key[0].
    """
    from app1.models.post import Post
    SLUG = 'apitest-post-create'
    new_id = None
    try:
        res = await apiclient.post('/api/posts', json={
            'slug': SLUG,
            'title': 'Post Create',
            'body': 'body',
            'creator_id': 1,
            'owner_id': 2,
        })
        assert res.status_code == 200, res.text
        created = res.json()
        assert created['slug'] == SLUG
        # The new auto-increment primary key must be a real integer, not a CursorResult
        assert isinstance(created['id'], int)
        new_id = created['id']

        # And it is actually persisted / fetchable through the API
        fetched = await apiclient.get(f'/api/posts/{new_id}')
        assert fetched.status_code == 200, fetched.text
        assert fetched.json()['title'] == 'Post Create'
    finally:
        for leaked in await Post.query().where('slug', SLUG).get():
            await leaked.delete()


@pytest.mark.asyncio
async def test_create_bulk_via_post(apiclient):
    """POST a list of new models; each comes back with its own integer primary key."""
    from app1.models.post import Post
    slugs = ['apitest-bulk-1', 'apitest-bulk-2']
    try:
        res = await apiclient.post('/api/posts', json=[
            {'slug': slugs[0], 'title': 'Bulk 1', 'body': 'b1', 'creator_id': 1, 'owner_id': 2},
            {'slug': slugs[1], 'title': 'Bulk 2', 'body': 'b2', 'creator_id': 1, 'owner_id': 2},
        ])
        assert res.status_code == 200, res.text
        created = res.json()
        assert isinstance(created, list) and len(created) == 2
        ids = [row['id'] for row in created]
        assert all(isinstance(i, int) for i in ids)
        assert ids[0] != ids[1]
    finally:
        for slug in slugs:
            for leaked in await Post.query().where('slug', slug).get():
                await leaked.delete()


@pytest.mark.asyncio
async def test_patch_ignores_relation_keys(apiclient):
    """PATCH updates scalar columns and silently ignores nested relation keys.

    A 'comments' key in the PATCH body must NOT create comments (relations are
    managed via /with_relations or the relation endpoints), and must not error.
    """
    from app1.models.post import Post
    from app1.models.comment import Comment

    post = await Post(slug='apitest-patch-rel', title='Before', body='b',
                      creator_id=1, owner_id=2).save()
    try:
        res = await apiclient.patch(f'/api/posts/{post.id}', json={
            'title': 'After',
            'comments': [{'title': 'should-be-ignored', 'body': 'x', 'creator_id': 1}],
        })
        assert res.status_code == 200, res.text

        # ...and the ignored relation is NOT echoed back in the response (it must not
        # leak unsaved raw dicts, which also tripped Pydantic v2's serializer).
        assert not res.json().get('comments')

        # Scalar updated...
        refreshed = await Post.query().find(post.id)
        assert refreshed.title == 'After'
        # ...relation ignored (no comment rows created for this post)
        assert len(await Comment.query().where('post_id', post.id).get()) == 0
    finally:
        leftover = await Post.query().find(post.id)
        if leftover:
            await leftover.delete()


@pytest.mark.asyncio
async def test_put_ignores_relation_keys(apiclient):
    """PUT replaces scalar columns and ignores nested relation keys."""
    from app1.models.post import Post
    from app1.models.comment import Comment

    post = await Post(slug='apitest-put-rel', title='Before', body='b',
                      creator_id=1, owner_id=2).save()
    try:
        res = await apiclient.put(f'/api/posts/{post.id}', json={
            'slug': 'apitest-put-rel',
            'title': 'Replaced',
            'body': 'newbody',
            'creator_id': 1,
            'owner_id': 2,
            'comments': [{'title': 'ignored', 'body': 'x', 'creator_id': 1}],
        })
        assert res.status_code == 200, res.text

        refreshed = await Post.query().find(post.id)
        assert refreshed.title == 'Replaced'
        assert refreshed.body == 'newbody'
        assert len(await Comment.query().where('post_id', post.id).get()) == 0
    finally:
        leftover = await Post.query().find(post.id)
        if leftover:
            await leftover.delete()
