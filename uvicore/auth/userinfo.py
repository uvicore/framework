import uvicore
from uvicore.typing import Dict
from uvicore.contracts import UserInfo as UserInfoInterface


@uvicore.service()
class UserInfo(UserInfoInterface):
    pass
