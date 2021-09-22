import pytest
import uvicore
from uvicore.support.dumper import dump
from tests.seeders import seed_post8


@pytest.mark.asyncio
async def Xtest_single(app1, client):
    # Delete single item by /{id} in url
    from app1.models import Post

    # Create a temp post we can delete
    await seed_post8()
    post = await Post.query().find(slug='test-post8')

    # HTTP DELETE /{id}
    res = await client.delete('/api/posts/' + str(post.id))
    assert res.status_code == 200, res.text
    # post = res.json()
    # dump(post)

    # Check normal seeded posts
    seeded_posts = ['test-post1', 'test-post2', 'test-post3', 'test-post4', 'test-post5', 'test-post6', 'test-post7'];
    posts = await Post.query().get()
    assert(seeded_posts == [x.slug for x in posts])


@pytest.mark.asyncio
async def test_where_query(app1, client):
    # Delete using a where query
    from app1.models import Post

    # Create a temp post we can delete
    await seed_post8()
    post = await Post.query().find(slug='test-post8')

    import httpx

    # Works
    # req = httpx.Request("DELETE", "http://testserver/api/comments", json={
    #     # {"post_id": [">", 1], "title": ["in", ["one", "two"]], "body": ["like", "%asdfasdf%"]}
    #     "where": {
    #         "post_id": ["=", 1],
    #         #"post_id": 1,
    #         #"title": ["in", ['one', 'two']],
    #         #"body": ["like", "%asdfasdf%"]
    #     },
    # })
    # res = await client.send(req)

    res = await client.delete("/api/comments", json={
        # {"post_id": [">", 1], "title": ["in", ["one", "two"]], "body": ["like", "%asdfasdf%"]}
        "where": {
            "post_id": ["=", 1],
            #"post_id": 1,
            #"title": ["in", ['one', 'two']],
            #"body": ["like", "%asdfasdf%"]
        },
    })
    #res = await client.send(req)





    dump(res)
    #assert res.status_code == 200, res.text
    #post = res.json()
    #dump(post)
    assert False
