import pytest
import uvicore
#from tests import bootstrap_app1, event_loop
from uvicore.support.dumper import dump
from starlette.testclient import TestClient



@pytest.mark.asyncio
async def test_app1(bootstrap_app1):
    #print(app.providers)

    #dump(uvicore.app.providers)

    #dump(uvicore.db.connections)

    from app1.models.post import Post
    from uvicore.auth.models.user import User
    #dump(Post.info())

    #metakey = 'sqlite:///:memory'

    users = await User.all()
    dump(users)




    # client = TestClient(uvicore.app.http.server)
    # #print(uvicore.app.http.server)
    # response = client.get('/app1/api/posts')
    # dump(response)

    #dump(client)




    #from uvicore.support import path
    #print(path.find_base(__file__) + '/testapp/app')
    assert 1 == 2
    #assert __version__ == '0.1.0'


