from __future__ import annotations
import uvicore
from typing import Optional
from uvicore.auth.database.tables import user_info as table
from uvicore.orm.fields import Field, BelongsTo
from uvicore.orm.metaclass import ModelMetaclass
from uvicore.orm.model import Model
from uvicore.support.dumper import dd, dump


from uvicore.auth.contracts import UserInfo as UserInfoInterface

class UserInfoModel(Model['UserInfoModel'], metaclass=ModelMetaclass):
#class UserModel(Model['UserModel']):
    """Auth User Model"""

    # Database connection and table information
    __tableclass__ = table.UserInfo

    id: Optional[int] = Field('id',
        primary=True,
        description='User Primary ID',
        sortable=True,
        searchable=True,
    )

    extra1: str = Field('extra1',
        description='Extra1',
    )

    user_id: int = Field('user_id',
        description="Contacts User ID",
        required=True,
    )

    # One-To-One Inverse - Contact has ONE User
    user: Optional[User] = Field(None,
        description="User Model",
        #belongs_to=('uvicore.auth.models.user.User', 'id', 'user_id'),
        #relation=BelongsTo('uvicore.auth.models.user.User', 'id', 'user_id')
        relation=BelongsTo('uvicore.auth.models.user.User')
    )

# IoC Class Instance
UserInfo: UserInfoModel = uvicore.ioc.make('uvicore.auth.models.user_info.UserInfo', UserInfoModel)
#class UserInfo(UserInfoIoc, Model[UserInfoModel], UserInfoInterface): pass

# class UserInfo(
#     _UserInfo,
#     Model[UserInfoModel],
#     UserInfoInterface
# ): pass


#from uvicore.auth.models.user import UserModel as User
#from uvicore.auth.models.user import User
User = uvicore.ioc.make('uvicore.auth.models.user.User')
UserInfo.update_forward_refs()
