from __future__ import annotations

from typing import Optional

import uvicore
from uvicore.auth.database.tables import users as table
#from uvicore.orm.fields import Field, HasOne
#from uvicore.orm.model import Model, ModelMetaclass
from uvicore.support.dumper import dd, dump
from uvicore.orm import Model, ModelMetaclass, Field, HasOne

#Model: _Model = uvicore.ioc.make('Model', _Model)
#import sys
#sys.modules['uvicore.orm.model']._Model = 'asdf'
#dump(sys.modules['uvicore.orm.model'].__dict__)

#from uvicore.orm.model import _Model
#dump(_Model)
#asdf('asdf')

# from abc import ABC, abstractmethod
# class UserInterface(ABC):
#     # @abstractmethod
#     # def idx(self) -> Optional[int]:
#     #     pass

#     id2: Optional[int]


#from uvicore.contracts import Model as ModelInterface
# # Model interfaces, though redundant, are used for proper type hinting code intellisense
# class User(ModelInterface):
#     id: Optional[int]
#     email: str
#     info: Optional[List[UserInfo]]


# UserModel for typehints only.  Import User for actual usage.
#class UserModel(Model, metaclass=ModelMetaclass):


#@uvicore.ioc.bind('uvicore.auth.models.user.User')

@uvicore.model()
class User(Model['User'], metaclass=ModelMetaclass):
#class UserModel(Model['UserModel']):
    """Auth User Model"""

    # Database connection and table information
    __tableclass__ = table.Users

    id: Optional[int] = Field('id',
        primary=True,
        description='User Primary ID',
        sortable=True,
        searchable=True,
    )

    email: str = Field('email',
        description='User Email and Username',
        required=True,
    )

    # One-To-One - User has ONE Contact
    info: Optional[UserInfo] = Field(None,
        description='User Info Model',
        relation=HasOne('uvicore.auth.models.user_info.UserInfo', foreign_key='user_id'),
    )

    # class Config:
    #     extra = 'ignore'
    #     arbitrary_types_allowed = True


# IoC Class Instance
#User = UserModel
#User: UserModel = uvicore.ioc.make('uvicore.auth.models.user.User', UserModel)
#User: UserModel = uvicore.ioc.make('uvicore.auth.models.user.User')
#class User(UserIoc, Model[UserModel], UserInterface): pass

# class User(
#     _User,
#     Model[_User],
#     UserInterface
# ): pass



from uvicore.auth.models.user_info import UserInfo  # isort:skip
#UserInfo = uvicore.ioc.make('uvicore.auth.models.user_info.UserInfo')
User.update_forward_refs()
