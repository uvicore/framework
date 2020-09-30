import pytest
import uvicore
from typing import List
from uvicore.support.dumper import dump

# Typechecking imports only
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app1.models.user import UserModel


@pytest.mark.asyncio
async def test_find(app1):
    from uvicore.auth.models.user import User
    user: UserModel = await User.find(3)
    dump(user)
    assert user.email == 'manager2@example.com'


@pytest.mark.asyncio
async def test_select_all(app1):
    from uvicore.auth.models.user import User
    users: List[UserModel] = await User.get()
    assert [
        'administrator@example.com',
        'manager1@example.com',
        'manager2@example.com',
        'user1@example.com',
        'user2@example.com',
    ] == [x.email for x in users]



