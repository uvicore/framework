"""
Regression tests for combining MULTIPLE *Many relations in a single ORM include.

Bug: each *Many secondary query joins all the other included *Many relations,
producing a cartesian product of raw rows.  The BelongsToMany / MorphToMany
result-combine iterated those raw rows and appended one entry per row, so a post
with 5 tags + 2 comments + 3 attributes + 4 hashtags came back with 5*2*3*4 = 120
tags and 120 hashtags.  Fixed by deduping the combine on the (left, right) pivot
pair.

Post 1 is seeded with: 2 comments (HasMany), 5 tags (BelongsToMany),
1 image (MorphOne), 3 attributes (MorphMany), 4 hashtags (MorphToMany).
"""
import pytest


@pytest.mark.asyncio
async def test_two_many_includes_do_not_multiply(app1):
    """Including two *Many relations (HasMany + BelongsToMany) keeps both correct."""
    from app1.models.post import Post
    post = await Post.query().include('comments', 'tags').find(1)
    assert len(post.comments) == 2
    assert [t.name for t in post.tags] == ['linux', 'mac', 'bsd', 'test1', 'test2']


@pytest.mark.asyncio
async def test_many_belongs_to_many_and_morph_to_many_together(app1):
    """BelongsToMany (tags) + MorphToMany (hashtags) together do not cartesian-multiply."""
    from app1.models.post import Post
    post = await Post.query().include('tags', 'hashtags').find(1)
    assert len(post.tags) == 5
    assert len(post.hashtags) == 4


@pytest.mark.asyncio
async def test_all_many_includes_together(app1):
    """All *Many relation kinds combined each return their own correct cardinality."""
    from app1.models.post import Post
    post = await Post.query().include('comments', 'tags', 'attributes', 'hashtags').find(1)

    assert len(post.comments) == 2                         # HasMany
    assert len(post.tags) == 5                             # BelongsToMany
    assert len(post.attributes) == 3                       # MorphMany (dict keyed by 'key')
    assert len(post.hashtags) == 4                         # MorphToMany

    # Tag/hashtag identities are intact (not duplicated)
    assert [t.name for t in post.tags] == ['linux', 'mac', 'bsd', 'test1', 'test2']
    assert sorted(post.attributes.keys()) == ['badge', 'post1-test1', 'post1-test2']


@pytest.mark.asyncio
async def test_many_includes_across_full_list(app1):
    """Combining *Many includes over a full .get() keeps every row's relations correct."""
    from app1.models.post import Post
    posts = await Post.query().include('comments', 'tags', 'hashtags').get()
    assert len(posts) == 7
    # Post 1: 5 tags, 4 hashtags, 2 comments
    assert len(posts[0].tags) == 5
    assert len(posts[0].hashtags) == 4
    assert len(posts[0].comments) == 2
    # Post 2: 2 tags (linux, bsd), no comments
    assert [t.name for t in posts[1].tags] == ['linux', 'bsd']
