import pytest
import uvicore
from fastapi.testclient import TestClient
from uvicore.support.dumper import dump


def Xtest_post_no_relations(app1):
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
    #post = res.json()
    #dump(post)
    assert False


def test_post_many_to_many_tags(app1):
    client = TestClient(uvicore.app.http)

    #from app1.models.tag import Tag
    #tags = await Tag.query().key_by('name').get()
    #dump(tags['linux'].dict())

    res = client.post("/api/posts", json={
        'slug': 'test-post9',
        'title': 'Test Post9',
        'body': 'This is the body for test post9.  I like the taste of water.',
        'creator_id': 1,
        'owner_id': 2,
        # 'tags': [
        #     {'id': 1, 'name': 'linux', 'creator_id': 1},
        #     {'id': 3, 'name': 'bsd', 'creator_id': 2},
        #     # Not work,
        #     #tags['linux'].dict(),
        #     #tags['bsd'].dict(),
        # ],
        'comments': [
            {
                'title': 'Post9 Comment1',
                'body': 'Body for post9 comment1',
                #'post_id': 1,  # No id needed, thats what post.create() does
                'creator_id': 1,
            }
        ],
    })
    assert res.status_code == 200, res.text
    post = res.json()
    dump(post)
    assert False
