import pytest
import uvicore
import json
from starlette.testclient import TestClient
from uvicore.support.dumper import dump

@pytest.mark.asyncio
async def test_list(app1, client):
    res = await client.get("/api/posts")
    assert res.status_code == 200, res.text

    posts = res.json()
    dump(posts)
    assert len(posts) == 7
    assert posts[0] == {
        'id': 1,
        'slug': 'test-post1',
        'title': 'Test Post1',
        'body': 'This is the body for test post1.  I like the color red and green.',
        'other': 'other stuff1',
        'cb': 'test-post1 callback',
        'creator_id': 1,
        'creator': None,
        'owner_id': 2,
        'owner': None,
        'comments': None,
        'tags': None,
        'image': None,
        'attributes': None,
        'hashtags': None
    }


# @pytest.mark.asyncio
# async def test_list_include_one_to_one(app1, client):
#     #res = client.get("/api/posts?include=creator.info,creator.contact,comments.creator.info,comments.contact,tags.creator,image,attributes,hashtags")
#     res = await client.get("/api/posts?include=creator.info")
#     assert res.status_code == 200, res.text
#     posts = res.json()

#     # Total of 7 posts
#     assert len(posts) == 7

#     # Test one post
#     # Remove fields that change per seed/test run
#     post = posts[0]
#     del post['creator']['created_at']
#     del post['creator']['updated_at']
#     del post['creator']['uuid']
#     dump(post)

#     assert post == {
#         'id': 1,
#         'slug': 'test-post1',
#         'title': 'Test Post1',
#         'body': 'This is the body for test post1.  I like the color red and green.',
#         'other': 'other stuff1',
#         'cb': 'test-post1 callback',
#         'creator_id': 1,
#         'creator': {
#             'id': 1,
#             #'uuid': 'a93ce457-15fe-46ce-a9e0-62c491acc746',
#             'username': 'anonymous',
#             'email': 'anonymous@example.com',
#             'first_name': 'Anonymous',
#             'last_name': 'User',
#             'title': 'Anonymous',
#             'avatar_url': None,
#             'password': None,
#             'disabled': True,
#             'creator_id': 1,
#             'creator': None,
#             #'created_at': '2021-09-01T16:59:51',
#             #'updated_at': '2021-09-01T16:59:51',
#             'login_at': None,
#             'groups': None,
#             'roles': None,
#             'app1_extra': None,
#             'info': {
#                 'id': 1,
#                 'extra1': 'user1 extra',
#                 'user_id': 1,
#                 'user': None
#             },
#             'contact': None,
#             'posts': None,
#             'image': None
#         },
#         'owner_id': 2,
#         'owner': None,
#         'comments': None,
#         'tags': None,
#         'image': None,
#         'attributes': None,
#         'hashtags': None
#     }
#     #assert False


# @pytest.mark.asyncio
# async def test_get_include_one_to_many(app1, client):
#     #res = client.get("/api/posts?include=creator.info,creator.contact,comments.creator.info,comments.contact,tags.creator,image,attributes,hashtags")
#     res = await client.get("/api/auth_users/1?include=posts.comments")
#     assert res.status_code == 200, res.text
#     user = res.json()
#     dump(user)

#     assert user['email'] == 'anonymous@example.com'
#     assert len(user['posts']) == 2
#     assert len(user['posts'][0]['comments']) == 2
#     assert len(user['posts'][1]['comments']) == 0


# @pytest.mark.asyncio
# async def test_list_where(app1, client):
#     # Where with include
#     res = await client.get('/api/posts?include=creator.info,owner.info&where={"creator_id":1}')
#     assert res.status_code == 200, res.text
#     posts = res.json()
#     dump(posts)

#     assert len(posts) == 2
#     assert posts[0]['slug'] == 'test-post1'
#     assert posts[0]['creator']['email'] == 'anonymous@example.com'
#     assert posts[0]['creator']['info']['extra1'] == 'user1 extra'
#     assert posts[0]['owner']['email'] == 'administrator@example.com'
#     assert posts[0]['owner']['info']['extra1'] == 'user2 extra'

#     assert posts[1]['slug'] == 'test-post2'
#     assert posts[0]['creator']['email'] == 'anonymous@example.com'
#     assert posts[0]['creator']['info']['extra1'] == 'user1 extra'
#     assert posts[0]['owner']['email'] == 'administrator@example.com'
#     assert posts[0]['owner']['info']['extra1'] == 'user2 extra'
#     # assert False


# @pytest.mark.asyncio
# async def test_list_where_ge_null(app1, client):
#     # Where AND with a >= and null
#     res = await client.get('/api/posts?where={"creator_id":[">=", 2], "other": "null"}')
#     assert res.status_code == 200, res.text
#     posts = res.json()
#     dump(posts)

#     assert len(posts) == 3
#     assert [
#         'test-post4',
#         'test-post5',
#         'test-post7',
#     ] == [x['slug'] for x in posts]
#     #assert False


# @pytest.mark.asyncio
# async def test_list_where_like(app1, client):
#     # Where LIKE
#     res = await client.get('/api/posts?where={"body": ["like", "%favorite%"]}')
#     assert res.status_code == 200, res.text
#     posts = res.json()
#     dump(posts)

#     assert len(posts) == 2
#     assert [
#         'test-post2',
#         'test-post4',
#     ] == [x['slug'] for x in posts]
#     #assert False


# @pytest.mark.asyncio
# async def test_list_where_in(app1, client):
#     # Where IN
#     res = await client.get('/api/posts?where={"creator_id": ["in", [1,5]]}')
#     assert res.status_code == 200, res.text
#     posts = res.json()
#     dump(posts)

#     assert len(posts) == 3
#     assert [
#         'test-post1',
#         'test-post2',
#         'test-post7',
#     ] == [x['slug'] for x in posts]
#     #assert False
