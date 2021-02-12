import pytest
import uvicore
from fastapi.testclient import TestClient
from uvicore.support.dumper import dump


def test_post(app1):
    client = TestClient(uvicore.app.http.server)

    res = client.post("/app1/api/hashtags", json={
        'name': 'test3'
    })

    dump(res)

    assert False
    #assert res.status_code == 200, res.text
    #data = res.json()
    #dump(data)

