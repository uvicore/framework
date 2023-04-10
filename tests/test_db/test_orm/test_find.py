import pytest
import uvicore
from typing import List
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_find(app1):
    from uvicore.auth.models.user import User
    user = await User.query().find(3)
    assert user.email == 'manager1@example.com'


@pytest.mark.asyncio
async def test_select_all(app1):
    from uvicore.auth.models.user import User
    users = await User.query().get()
    dump(users)
    assert [
        'anonymous@example.com',
        'administrator@example.com',
        'manager1@example.com',
        'manager2@example.com',
        'user1@example.com',
        'user2@example.com',
    ] == [x.email for x in users]



