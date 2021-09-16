import pytest
import uvicore
from fastapi.testclient import TestClient
from uvicore.support.dumper import dump


def Xtest_single(app1):
    client = TestClient(uvicore.app.http)

    res = client.post("/api/posts", json={
        'slug': 'test-post8',
        'title': 'Test Post8',
        'body': 'This is the body for test post8.  I like the taste of water.',
        #'other': 'other stuff1',
        #'cb': 'test-post1 callback',
        'creator_id': 1,
        #'creator': None,
        'owner_id': 2,
        #'owner': None,
        #'comments': None,
        #'tags': None,
        #'image': None,
        #'attributes': None,
        #'hashtags': None
    })
    assert res.status_code == 200, res.text
    post = res.json()
    dump(post)
    #assert False


def Xtest_bulk(app1):
    client = TestClient(uvicore.app.http)

    res = client.post("/api/posts", json=[
        {
            'slug': 'test-post9',
            'title': 'Test Post9',
            'body': 'This is the body for test post9.  I like the taste of water.',
            'creator_id': 1,
            'owner_id': 2,
        },
        {
            'slug': 'test-post10',
            'title': 'Test Post10',
            'body': 'This is the body for test post10.  I like the taste of water.',
            'creator_id': 1,
            'owner_id': 2,
        },
    ])
    assert res.status_code == 200, res.text
    post = res.json()
    dump(post)
    #assert False


def Xtest_single_relations_many_to_many(app1):
    client = TestClient(uvicore.app.http)

    # Cannot use await with TestClient for some reason, loop already started
    # So use API go get tags
    res = client.get("/api/tags")
    tags = {x['name']:x for x in res.json()}

    res = client.post("/api/posts/with_relations", json={
        'slug': 'test-post11',
        'title': 'Test Post11',
        'body': 'This is the body for test post11.  I like the taste of water.',
        'creator_id': 1,
        'owner_id': 2,
        'tags': [
            #{'id': 1, 'name': 'linux', 'creator_id': 1},
            #{'id': 3, 'name': 'bsd', 'creator_id': 2},
            tags['linux'],
            tags['bsd'],
        ],
        'comments': [
            {
                'title': 'Post11 Comment1',
                'body': 'Body for post11 comment1',
                #'post_id': 1,  # No id needed, thats what post.create() does
                'creator_id': 1,
            }
        ],
    })
    assert res.status_code == 200, res.text
    post = res.json()
    dump(post)
    #assert False


def Xtest_bulk_relations_many_to_many(app1):
    client = TestClient(uvicore.app.http)

    # Cannot use await with TestClient for some reason, loop already started
    # So use API go get tags
    res = client.get("/api/tags")
    tags = {x['name']:x for x in res.json()}

    res = client.post("/api/posts/with_relations", json=[
        {
            'slug': 'test-post12',
            'title': 'Test Post12',
            'body': 'This is the body for test post12.  I like the taste of water.',
            'creator_id': 1,
            'owner_id': 2,
            'tags': [
                tags['laravel'],
                tags['lumen'],
            ],
            'comments': [
                {
                    'title': 'Post12 Comment1',
                    'body': 'Body for post12 comment1',
                    #'post_id': 1,  # No id needed, thats what post.create() does
                    'creator_id': 1,
                }
            ],
        },
        {
            'slug': 'test-post13',
            'title': 'Test Post13',
            'body': 'This is the body for test post13.  I like the taste of water.',
            'creator_id': 1,
            'owner_id': 2,
            'tags': [
                tags['fastapi'],
                tags['starlette'],
            ],
            'comments': [
                {
                    'title': 'Post13 Comment1',
                    'body': 'Body for post13 comment1',
                    #'post_id': 1,  # No id needed, thats what post.create() does
                    'creator_id': 1,
                }
            ],
        },
    ])
    assert res.status_code == 200, res.text
    post = res.json()
    dump(post)
    #assert False
