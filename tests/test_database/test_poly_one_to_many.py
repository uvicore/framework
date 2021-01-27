import pytest
import uvicore
import sqlalchemy as sa
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_orm(app1):
    from app1.models.post import Post
    from app1.models.user import User

    # Get all
    query = Post.query().include('attributes')
    assert query.sql() == {
        'main': 'SELECT DISTINCT posts.id, posts.unique_slug, posts.title, posts.body, posts.other, posts.creator_id, posts.owner_id FROM posts LEFT OUTER JOIN attributes ON attributes.attributable_type = :attributable_type_1 AND posts.id = attributes.attributable_id',
        'attributes': 'SELECT DISTINCT attributes.id AS "attributes__id", attributes.attributable_type AS "attributes__attributable_type", attributes.attributable_id AS "attributes__attributable_id", attributes.key AS "attributes__key", attributes.value AS "attributes__value" FROM posts LEFT OUTER JOIN attributes ON attributes.attributable_type = :attributable_type_1 AND posts.id = attributes.attributable_id WHERE attributes.id IS NOT NULL'
    }
    posts = await query.get()
    pa = {x.id:x.attributes for x in posts}
    assert pa[1]['post1-test1'] == 'value for post1-test1' and len(pa[1]) == 3
    assert pa[1]['post1-test1'] == 'value for post1-test1' and len(pa[3]) == 1
    assert pa[2]['post2-test1'] == 'value for post2-test1' and len(pa[2]) == 3
    assert pa[6]['post6-test1'] == 'value for post6-test1' and len(pa[6]) == 4
    assert pa[4] == pa[5] == pa[7] == {}

    # Access attributes as a dict
    assert posts[0].attributes['badge'] == 'IT'

    # Filter posts based on a post attribute
    # Using actual standard where key and value
    posts = await (Post.query()
        .include('attributes')
        .where([
            ('attributes.key', '=', 'badge'),
            ('attributes.value', 'IT'),
        ])
        .get()
    )
    assert len(posts[0].attributes) == 3
    assert len(posts[1].attributes) == 3
    assert len(posts[2].attributes) == 4
    assert [1, 2, 6] == [x.id for x in posts]

    # Filter posts based on a post attribute
    # This is using the experimental dict_where feature
    posts = await (Post.query().include('attributes').where('attributes.post1-test1', 'value for post1-test1').get())
    assert len(posts) == 1
    assert posts[0].id == 1


    # Test poly one-to-many through a one-to-many
    users = await User.query().include('posts', 'posts.attributes').get()
    assert len(users) == 5
    assert len(users[4].posts) == 2
    assert len(users[4].posts[0].attributes) == 4


@pytest.mark.asyncio
async def Xtest_builder(app1):
    # FIXME, make it look exactly like the ORM version above
    pass


@pytest.mark.asyncio
async def Xtest_hybrid(app1):
    # FIXME, make it look exactly like the ORM version above
    pass


@pytest.mark.asyncio
async def Xtest_sqlalchemy(app1):
    # FIXME, make it look exactly like the ORM version above
    pass
