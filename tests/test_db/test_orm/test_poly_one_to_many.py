import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_get(app1):
    # Get all
    from app1.models.post import Post
    query = Post.query().include('attributes')
    # Probably not as this could be dialect specific
    # assert query.sql() == {
    #     'main': 'SELECT DISTINCT posts.id, posts.unique_slug, posts.title, posts.body, posts.other, posts.creator_id, posts.owner_id FROM posts LEFT OUTER JOIN attributes ON attributes.attributable_type = :attributable_type_1 AND posts.id = attributes.attributable_id',
    #     'attributes': 'SELECT DISTINCT attributes.id AS "attributes__id", attributes.attributable_type AS "attributes__attributable_type", attributes.attributable_id AS "attributes__attributable_id", attributes.key AS "attributes__key", attributes.value AS "attributes__value" FROM posts LEFT OUTER JOIN attributes ON attributes.attributable_type = :attributable_type_1 AND posts.id = attributes.attributable_id WHERE attributes.id IS NOT NULL'
    # }
    posts = await query.order_by('id').get()
    dump(posts)
    pa = {x.id:x.attributes for x in posts}
    assert pa[1]['post1-test1'] == 'value for post1-test1' and len(pa[1]) == 3
    assert pa[1]['post1-test1'] == 'value for post1-test1' and len(pa[3]) == 1
    assert pa[2]['post2-test1'] == 'value for post2-test1' and len(pa[2]) == 3
    assert pa[6]['post6-test1'] == 'value for post6-test1' and len(pa[6]) == 4
    assert pa[4] == pa[5] == pa[7] == {}

    # Access attributes as a dict
    assert posts[0].attributes['badge'] == 'IT'


@pytest.mark.asyncio
async def test_where_attribute(app1):
    # Filter posts based on a post attribute
    # Using actual standard where key and value
    from app1.models.post import Post
    posts = await (Post.query()
        .include('attributes')
        .where([
            ('attributes.key', '=', 'badge'),
            ('attributes.value', 'IT'),
        ])
        .order_by('id')
        .get()
    )
    dump(posts)
    assert len(posts[0].attributes) == 3
    assert len(posts[1].attributes) == 3
    assert len(posts[2].attributes) == 4
    assert [1, 2, 6] == [x.id for x in posts]


@pytest.mark.asyncio
async def test_where_attribute_dict(app1):
    # Filter posts based on a post attribute
    # This is using the experimental dict_where feature
    from app1.models.post import Post
    posts = await (Post.query()
        .include('attributes')
        .where('attributes.post1-test1', 'value for post1-test1')
        .order_by('id')
        .get()
    )
    dump(posts)
    assert len(posts) == 1
    assert posts[0].id == 1


@pytest.mark.asyncio
async def test_through_one_to_many(app1):
    # Test poly one-to-many through a one-to-many
    # A user has many posts, a post has many attributes
    from app1.models.user import User
    users = await User.query().include('posts', 'posts.attributes').order_by('id').get()
    dump(users[0])
    assert len(users) == 6
    assert len(users[0].posts) == 2
    assert len(users[0].posts[0].attributes) == 3
    assert len(users[0].posts[1].attributes) == 3


@pytest.mark.asyncio
async def test_through_one_to_many_inverse(app1):
    # Test poly one-to-many through a one-to-many inverse
    # A comment has ONE post, a post has many attributes
    from app1.models.comment import Comment
    comments = await Comment.query().include('post.attributes').where('post_id', '<=', 2).order_by('id').get()
    dump(comments[0])
    assert len(comments) == 2
    assert comments[0].post.id == 1
    assert len(comments[0].post.attributes) == 3
