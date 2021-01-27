import pytest
import uvicore
from fastapi.testclient import TestClient
from starlette.testclient import TestClient as X

from uvicore.support.dumper import dump


def test_get(app1):
    client = TestClient(uvicore.app.http.server)

    res = client.get("/app1/api/posts")
    assert res.status_code == 200, res.text
    data = res.json()
    assert len(data) == 7
    assert data[0] == {
        'id': 1,
        'slug': 'test-post1',
        'title': 'Test Post1',
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
    client = TestClient(uvicore.app.http.server)

    res = client.get("/app1/api/posts?include=creator.info,creator.contact,comments.creator.info,comments.contact,tags.creator,image,attributes,hashtags")
    assert res.status_code == 200, res.text
    data = res.json()
    assert len(data) == 7




    dump(res)

    assert False
