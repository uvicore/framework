import pytest
import uvicore
import json
from starlette.testclient import TestClient

from uvicore.support.dumper import dump


def Xtest_get(app1):
    client = TestClient(uvicore.app.http)
    res = client.get("/api/posts")
    assert res.status_code == 200, res.text
    data = res.json()
    dump(data)
    assert len(data) == 7
    assert data[0] == {
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


def Xtest_get_include_one_to_one(app1):
    client = TestClient(uvicore.app.http)

    #res = client.get("/api/posts?include=creator.info,creator.contact,comments.creator.info,comments.contact,tags.creator,image,attributes,hashtags")
    res = client.get("/api/posts?include=creator.info")
    assert res.status_code == 200, res.text
    data = res.json()

    # Total of 7 posts
    assert len(data) == 7

    # Test one post
    # Remove fields that change per seed/test run
    results = data[0]
    del results['creator']['created_at']
    del results['creator']['updated_at']
    del results['creator']['uuid']
    dump(results)

    assert results == {
        'id': 1,
        'slug': 'test-post1',
        'title': 'Test Post1',
        'body': 'This is the body for test post1.  I like the color red and green.',
        'other': 'other stuff1',
        'cb': 'test-post1 callback',
        'creator_id': 1,
        'creator': {
            'id': 1,
            #'uuid': 'a93ce457-15fe-46ce-a9e0-62c491acc746',
            'username': 'anonymous',
            'email': 'anonymous@example.com',
            'first_name': 'Anonymous',
            'last_name': 'User',
            'title': 'Anonymous',
            'avatar_url': None,
            'password': None,
            'disabled': True,
            'creator_id': 1,
            'creator': None,
            #'created_at': '2021-09-01T16:59:51',
            #'updated_at': '2021-09-01T16:59:51',
            'login_at': None,
            'groups': None,
            'roles': None,
            'app1_extra': None,
            'info': {
                'id': 1,
                'extra1': 'user1 extra',
                'user_id': 1,
                'user': None
            },
            'contact': None,
            'posts': None,
            'image': None
        },
        'owner_id': 2,
        'owner': None,
        'comments': None,
        'tags': None,
        'image': None,
        'attributes': None,
        'hashtags': None
    }
    #assert False

def test_get_include_one_to_many(app1):
    client = TestClient(uvicore.app.http)

    #res = client.get("/api/posts?include=creator.info,creator.contact,comments.creator.info,comments.contact,tags.creator,image,attributes,hashtags")
    res = client.get("/api/auth_users/1?include=posts.comments")
    assert res.status_code == 200, res.text
    user = res.json()
    dump(user)

    assert user['email'] == 'anonymous@example.com'
    #assert len(user['posts'] == 2)
    #assert len(user['posts'][0]['comments'] == 2)
    #assert len(user['posts'][1]['comments'] == 0)

    # # Total of 7 posts
    # assert len(data) == 7

    # Test one post
    # Remove fields that change per seed/test run
    #results = data[0]
    #del results['creator']['created_at']
    #del results['creator']['updated_at']
    #del results['creator']['uuid']

    #assert False

