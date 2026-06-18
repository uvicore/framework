"""
Dialect-agnostic end-to-end integration tests for the database + ORM layers.

These run against WHATEVER backend the app1 connection is configured for: the
default unit run exercises in-memory SQLite, and ./bin/test-integration.sh points
both the app1 and auth connections at a real Postgres / MySQL / MariaDB server.

All assertions are written to be portable across engines:
  * results are compared as sets or after an explicit .order_by() (Postgres/MySQL
    do not guarantee row order without ORDER BY, unlike SQLite's implicit order),
  * case-insensitive matching uses ilike (SQLite LIKE is case-insensitive, but
    Postgres LIKE is case-sensitive per the SQL standard),
  * inserts rely on database-generated primary keys (no SQLite NULL-pk quirk).

Seeded posts: ids 1-7, `other` set on 1,3,6 and NULL on 2,4,5,7.
"""
import pytest


async def ids(qb):
    return sorted(r.id for r in await qb.get())


# --------------------------------------------------------------------------
# Connectivity / schema
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_connection_is_configured(app1):
    import uvicore
    conn = uvicore.db.connection('app1')
    assert conn.dialect in ('sqlite', 'postgresql', 'mysql', 'mariadb')
    # The full seeded schema is queryable on whatever engine we are running
    from app1.models.post import Post
    assert len(await Post.query().get()) == 7


# --------------------------------------------------------------------------
# CRUD with a database-generated primary key (the cross-dialect insert fix)
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_insert_autoincrement_and_delete(app1):
    from app1.models.post import Post
    post = await Post(slug='xdb-crud', title='X', body='b', creator_id=1, owner_id=2).save()
    try:
        assert isinstance(post.id, int) and post.id > 0      # DB generated the pk
        again = await Post.query().find(post.id)
        assert again is not None and again.slug == 'xdb-crud'
        again.title = 'X2'
        await again.save()
        assert (await Post.query().find(post.id)).title == 'X2'
    finally:
        await post.delete()
    assert await Post.query().find(post.id) is None


# --------------------------------------------------------------------------
# Operator matrix (portable)
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_operators_portable(app1):
    from app1.models.post import Post
    assert await ids(Post.query().where('id', '=', 1)) == [1]
    assert await ids(Post.query().where('id', '!=', 1)) == [2, 3, 4, 5, 6, 7]
    assert await ids(Post.query().where('id', '>=', 5)) == [5, 6, 7]
    assert await ids(Post.query().where('id', 'in', [1, 3, 5])) == [1, 3, 5]
    assert await ids(Post.query().where('id', 'not in', [1, 3, 5])) == [2, 4, 6, 7]
    assert await ids(Post.query().where('id', 'between', [2, 4])) == [2, 3, 4]
    assert await ids(Post.query().where('other', 'is', None)) == [2, 4, 5, 7]
    assert await ids(Post.query().where('other', 'is not', None)) == [1, 3, 6]


@pytest.mark.asyncio
async def test_like_is_case_sensitive_ilike_is_not(app1):
    """LIKE semantics differ by engine; ILIKE is the portable case-insensitive form."""
    from app1.models.post import Post
    # Exact-case LIKE matches on every engine
    assert await ids(Post.query().where('title', 'like', '%Post1')) == [1]
    # ILIKE is case-insensitive everywhere (lowercase pattern still matches 'Test Post1')
    assert await ids(Post.query().where('title', 'ilike', '%post1')) == [1]
    assert await ids(Post.query().where('title', 'ilike', '%TEST%')) == [1, 2, 3, 4, 5, 6, 7]


@pytest.mark.asyncio
async def test_and_or_combinations(app1):
    from app1.models.post import Post
    assert await ids(Post.query().where('creator_id', 2).where('owner_id', 1)) == [3, 4]
    assert await ids(Post.query().or_where([('id', 1), ('id', 7)])) == [1, 7]
    assert await ids(Post.query().where('owner_id', 2).or_where([('id', 1), ('id', 5)])) == [1, 5]


@pytest.mark.asyncio
async def test_order_limit_offset(app1):
    from app1.models.post import Post
    desc = [p.id for p in await Post.query().order_by('id', 'DESC').get()]
    assert desc == [7, 6, 5, 4, 3, 2, 1]
    page = [p.id for p in await Post.query().order_by('id').limit(2).offset(2).get()]
    assert page == [3, 4]
    assert await Post.query().count() == 7


# --------------------------------------------------------------------------
# Relations (compared order-independently)
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_relations_portable(app1):
    from app1.models.post import Post
    post = await Post.query().include('creator', 'comments', 'tags', 'hashtags', 'attributes').find(1)
    # BelongsTo
    assert post.creator is not None
    # HasMany
    assert len(post.comments) == 2
    # BelongsToMany + MorphToMany (order not guaranteed -> compare as sets)
    assert {t.name for t in post.tags} == {'linux', 'mac', 'bsd', 'test1', 'test2'}
    assert {h.name for h in post.hashtags} == {'important', 'outdated', 'test1', 'test2'}
    # MorphMany returning a dict keyed by 'key'
    assert set(post.attributes.keys()) == {'badge', 'post1-test1', 'post1-test2'}


@pytest.mark.asyncio
async def test_multiple_many_includes_no_cartesian(app1):
    """Regression: combining several *Many includes must not multiply rows on any engine."""
    from app1.models.post import Post
    post = await Post.query().include('comments', 'tags', 'hashtags', 'attributes').find(1)
    assert len(post.comments) == 2
    assert len(post.tags) == 5
    assert len(post.hashtags) == 4
    assert len(post.attributes) == 3
