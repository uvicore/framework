import pytest
import uvicore
from fastapi.testclient import TestClient
from uvicore.support.dumper import dump


def test_single(app1):
    client = TestClient(uvicore.app.http)
    res = client.delete("/api/posts/7")
    assert res.status_code == 200, res.text
    post = res.json()
    dump(post)
    assert False
