import pytest
import uvicore
import json
from starlette.testclient import TestClient

from uvicore.support.dumper import dump


def test_get(app1):
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


def test_get_include(app1):
    client = TestClient(uvicore.app.http)

    #res = client.get("/api/posts?include=creator.info,creator.contact,comments.creator.info,comments.contact,tags.creator,image,attributes,hashtags")
    res = client.get("/api/posts?include=creator?include=creator.info")
    assert res.status_code == 200, res.text
    data = res.json()

    # Total of 7 posts
    assert len(data) == 7

    # Test one post
    # Remove fields that change per seed/test run
    results = data[0]
    # del results['creator']['created_at']
    # del results['creator']['updated_at']
    # del results['creator']['uuid']

    dump(results)

    # assert results == {
    #     'id': 1,
    #     'slug': 'test-post1',
    #     'title': 'Test Post1',
    #     'body': 'This is the body for test post1.  I like the color red and green.',
    #     'other': 'other stuff1',
    #     'cb': 'test-post1 callback',
    #     'creator_id': 1,
    #     'creator': {
    #         'id': 1,
    #         'username': 'anonymous',
    #         'email': 'anonymous@example.com',
    #         'first_name': 'Anonymous',
    #         'last_name': 'User',
    #         'title': 'Anonymous',
    #         'avatar_url': None,
    #         'password': None,
    #         'disabled': True,
    #         'creator_id': 1,
    #         'creator': None,
    #         'login_at': None,
    #         'groups': None,
    #         'roles': None,
    #         'app1_extra': None,
    #         'info': None,
    #         'contact': None,
    #         'posts': None,
    #         'image': None
    #     },
    #     'owner_id': 2,
    #     'owner': None,
    #     'comments': None,
    #     'tags': None,
    #     'image': None,
    #     'attributes': None,
    #     'hashtags': None
    # }
    assert False

