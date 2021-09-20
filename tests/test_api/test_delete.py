import pytest
import uvicore
from fastapi.testclient import TestClient
from uvicore.support.dumper import dump


def Xtest_single(app1):
    client = TestClient(uvicore.app.http)
    res = client.delete("/api/posts/1")

    # res = client.delete("/api/posts", json={
    #     # {"post_id": [">", 1], "title": ["in", ["one", "two"]], "body": ["like", "%asdfasdf%"]}
    #     "where": {
    #         "post_id": [">", 1],
    #         #"title": ["in", ['one', 'two']],
    #         #"body": ["like", "%asdfasdf%"]
    #     },
    #     "unlink": ['tags']
    # })
    assert res.status_code == 200, res.text
    post = res.json()
    dump(post)
    assert False


def test_multi_query(app1):
    client = TestClient(uvicore.app.http)
    res = client.delete("/api/comments", json={
        # {"post_id": [">", 1], "title": ["in", ["one", "two"]], "body": ["like", "%asdfasdf%"]}
        "where": {
            "post_id": [">=", 1],
            #"post_id": 1,
            #"title": ["in", ['one', 'two']],
            #"body": ["like", "%asdfasdf%"]
        },
    })
    assert res.status_code == 200, res.text
    post = res.json()
    dump(post)
    assert False
