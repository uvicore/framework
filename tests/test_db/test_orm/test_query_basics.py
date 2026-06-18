"""
Basic ORM query-builder behaviors: limit, offset, order_by, distinct and model
attribute access.

Consolidated here (the canonical ORM test home under test_db/) from the former
shallow tests/test_orm/test_model_methods.py and tests/test_orm_queries.py, with
real result assertions instead of import/`is not None` checks. Where-operator and
relation behavior are covered by the sibling test_where_operators.py and
test_rel_*/test_poly_* modules.

Seeded posts: ids 1-7.
"""
import pytest


@pytest.mark.asyncio
async def test_limit(app1):
    from app1.models.post import Post
    posts = await Post.query().order_by('id').limit(3).get()
    assert [p.id for p in posts] == [1, 2, 3]


@pytest.mark.asyncio
async def test_offset(app1):
    from app1.models.post import Post
    page1 = await Post.query().order_by('id').limit(2).get()
    page2 = await Post.query().order_by('id').limit(2).offset(2).get()
    assert [p.id for p in page1] == [1, 2]
    assert [p.id for p in page2] == [3, 4]


@pytest.mark.asyncio
async def test_order_by_asc_and_desc(app1):
    from app1.models.post import Post
    asc = [p.id for p in await Post.query().order_by('id').get()]
    desc = [p.id for p in await Post.query().order_by('id', 'DESC').get()]
    assert asc == [1, 2, 3, 4, 5, 6, 7]
    assert desc == [7, 6, 5, 4, 3, 2, 1]


@pytest.mark.asyncio
async def test_distinct_executes_and_returns_unique_rows(app1):
    from app1.models.post import Post
    posts = await Post.query().distinct().order_by('id').get()
    ids = [p.id for p in posts]
    assert ids == [1, 2, 3, 4, 5, 6, 7]
    assert len(ids) == len(set(ids))


@pytest.mark.asyncio
async def test_model_attribute_access(app1):
    from app1.models.post import Post
    post = await Post.query().find(1)
    assert post.id == 1
    assert post.slug == 'test-post1'
    assert isinstance(post.title, str)


@pytest.mark.asyncio
async def test_count(app1):
    from app1.models.post import Post
    assert await Post.query().count() == 7
    assert await Post.query().where('creator_id', 2).count() == 3
