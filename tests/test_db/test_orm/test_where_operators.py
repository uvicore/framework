"""
Comprehensive where / or_where operator matrix for the ORM query builder.

The ORM builder inherits the where engine from the low-level DbQueryBuilder, so
these also validate uvicore/database/builder.py _where_expression. Seeded posts
(ids 1-7) have `other` set on 1,3,6 and NULL on 2,4,5,7.
"""
import pytest


async def ids(qb):
    rows = await qb.order_by('id').get()
    return [r.id for r in rows]


# --------------------------------------------------------------------------
# Equality / inequality
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_equality_operators(app1):
    from app1.models.post import Post
    assert await ids(Post.query().where('id', '=', 1)) == [1]
    assert await ids(Post.query().where('id', '==', 1)) == [1]
    assert await ids(Post.query().where('id', 1)) == [1]                 # default operator is =
    assert await ids(Post.query().where('id', '!=', 1)) == [2, 3, 4, 5, 6, 7]
    assert await ids(Post.query().where('id', '<>', 1)) == [2, 3, 4, 5, 6, 7]


@pytest.mark.asyncio
async def test_comparison_operators(app1):
    from app1.models.post import Post
    assert await ids(Post.query().where('id', '>', 5)) == [6, 7]
    assert await ids(Post.query().where('id', '>=', 5)) == [5, 6, 7]
    assert await ids(Post.query().where('id', '<', 3)) == [1, 2]
    assert await ids(Post.query().where('id', '<=', 3)) == [1, 2, 3]


# --------------------------------------------------------------------------
# IN / NOT IN (and natural-language + case-insensitive variants)
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_in_and_not_in(app1):
    from app1.models.post import Post
    assert await ids(Post.query().where('id', 'in', [1, 3, 5])) == [1, 3, 5]
    assert await ids(Post.query().where('id', '!in', [1, 3, 5])) == [2, 4, 6, 7]
    assert await ids(Post.query().where('id', 'not in', [1, 3, 5])) == [2, 4, 6, 7]
    # operator is case-insensitive and whitespace tolerant
    assert await ids(Post.query().where('id', 'IN', [1, 3, 5])) == [1, 3, 5]
    assert await ids(Post.query().where('id', 'Not  In', [1, 3, 5])) == [2, 4, 6, 7]


# --------------------------------------------------------------------------
# LIKE / NOT LIKE / ILIKE
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_like_variants(app1):
    from app1.models.post import Post
    assert await ids(Post.query().where('title', 'like', '%Post1')) == [1]
    assert await ids(Post.query().where('title', '!like', '%Post1')) == [2, 3, 4, 5, 6, 7]
    assert await ids(Post.query().where('title', 'not like', '%Post1')) == [2, 3, 4, 5, 6, 7]
    # ilike is case-insensitive (lowercase pattern still matches 'Test Post1')
    assert await ids(Post.query().where('title', 'ilike', '%post1')) == [1]
    assert await ids(Post.query().where('title', '!ilike', '%post1')) == [2, 3, 4, 5, 6, 7]


# --------------------------------------------------------------------------
# BETWEEN / NOT BETWEEN
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_between(app1):
    from app1.models.post import Post
    assert await ids(Post.query().where('id', 'between', [2, 4])) == [2, 3, 4]
    assert await ids(Post.query().where('id', 'not between', [2, 4])) == [1, 5, 6, 7]


# --------------------------------------------------------------------------
# NULL handling: explicit is/is not, the 'null' magic string, and Python None
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_null_handling(app1):
    from app1.models.post import Post
    assert await ids(Post.query().where('other', 'is', None)) == [2, 4, 5, 7]
    assert await ids(Post.query().where('other', 'is not', None)) == [1, 3, 6]
    assert await ids(Post.query().where('other', 'is null', None)) == [2, 4, 5, 7]
    assert await ids(Post.query().where('other', 'is not null', None)) == [1, 3, 6]
    assert await ids(Post.query().where('other', '=', 'null')) == [2, 4, 5, 7]   # magic string
    assert await ids(Post.query().where('other', '=', None)) == [2, 4, 5, 7]     # == None -> IS NULL
    assert await ids(Post.query().where('other', '!=', None)) == [1, 3, 6]       # != None -> IS NOT NULL


# --------------------------------------------------------------------------
# AND (chained wheres) / OR (or_where) / combined
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_and_chained_wheres(app1):
    from app1.models.post import Post
    # creator_id=2 AND owner_id=1  -> posts 3,4
    assert await ids(Post.query().where('creator_id', 2).where('owner_id', 1)) == [3, 4]


@pytest.mark.asyncio
async def test_or_where(app1):
    from app1.models.post import Post
    assert await ids(Post.query().or_where([('id', 1), ('id', 7)])) == [1, 7]
    # or_where with explicit operators
    assert await ids(Post.query().or_where([('id', '<', 2), ('id', '>', 6)])) == [1, 7]


@pytest.mark.asyncio
async def test_and_combined_with_or_group(app1):
    from app1.models.post import Post
    # owner_id=2 AND (id=1 OR id=5)  -> posts 1 and 5 (both owned by 2)
    result = await ids(Post.query().where('owner_id', 2).or_where([('id', 1), ('id', 5)]))
    assert result == [1, 5]
    # creator_id=2 AND (id=1 OR id=7) -> none (1 and 7 are not creator 2)
    assert await ids(Post.query().where('creator_id', 2).or_where([('id', 1), ('id', 7)])) == []


# --------------------------------------------------------------------------
# Clear errors (robustness) instead of silent wrong results / cryptic crashes
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_unknown_operator_raises_clear_error(app1):
    from app1.models.post import Post
    with pytest.raises(Exception, match='Unsupported where operator'):
        await Post.query().where('id', 'frobnicate', 1).get()


@pytest.mark.asyncio
async def test_unknown_column_raises_clear_error(app1):
    from app1.models.post import Post
    with pytest.raises(Exception, match='was not found'):
        await Post.query().where('nonexistent_column', '=', 1).get()
