from __future__ import annotations

from typing import Optional

import uvicore
from uvicore.auth.database.tables import user_info as table
#from uvicore.orm.fields import BelongsTo, Field
#from uvicore.orm.model import Model, ModelMetaclass
from uvicore.support.dumper import dd, dump
from uvicore.orm import Model, ModelMetaclass, Field, BelongsTo

#@uvicore.ioc.bind('uvicore.auth.models.user_info.UserInfo')
#class UserInfoModel(Model['UserInfoModel'], metaclass=ModelMetaclass):

@uvicore.model()
class UserInfo(Model['UserInfo'], metaclass=ModelMetaclass):
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
#UserInfo: UserInfoModel = uvicore.ioc.make('uvicore.auth.models.user_info.UserInfo', UserInfoModel)
#class UserInfo(UserInfoIoc, Model[UserInfoModel], UserInfoInterface): pass

# class UserInfo(
#     _UserInfo,
#     Model[UserInfoModel],
#     UserInfoInterface
# ): pass


#from uvicore.auth.models.user import UserModel as User  # isort:skip
from uvicore.auth.models.user import User  # isort:skip
#User = uvicore.ioc.make('uvicore.auth.models.user.User')
UserInfo.update_forward_refs()
