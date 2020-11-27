import pytest
import sqlalchemy as sa

import uvicore
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_orm(app1):
    from app1.models.post import Post

    posts = await Post.query().include('attributes').get()


    # Works, limits actual post
    # posts = await Post.query().include('attributes').where([
    #     ('attributes.key', 'post1-test1'),
    #     ('attributes.value', 'value for post1-test1'),
    # ]).order_by('id').get()

    # What I want
    #posts = await Post.query().include('attributes').where('attribute.post1-test1', 'value for post1-test1').get()
    #posts = await Post.query().whereAttribute('dms', 'adp')


    # Works, shows all posts but filters attributes
    #posts = await Post.query().include('attributes').filter('attributes.key', 'post1-test1').filter('attributes.value', 'value for post1-test1').get()

    dump(posts)

    # What I want
    # for post in posts:
    #     if 'post1-test1' in post.attributes:
    #         dump(post.attributes.get('post1-test1'))


    assert False
