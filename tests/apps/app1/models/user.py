from __future__ import annotations

from typing import List, Optional

import uvicore
from uvicore.auth.database.tables import users as table
from uvicore.orm.fields import Field, HasMany, HasOne
from uvicore.orm.metaclass import ModelMetaclass
from uvicore.orm.model import Model
from uvicore.contracts import Model as ModelInterface
from uvicore.support.dumper import dd, dump


#from typing import TYPE_CHECKING
#if TYPE_CHECKING:
#from app1.models.contact import Contact

#from app1.models.contact import Contact
#from app1.models import contact
#Contact = uvicore.ioc.make('app1.models.Contact')


# This is an override.  Do not import this Model, instead import
# the original in uvicore.auth.models
#class UserModel(AuthOverride):

# class UserInterface(ModelInterface):
#     id: Optional[int]
#     email: str
#     app1_extra: Optional[str]
#     contact: 'Optional[ContactModel]'
#     posts: 'Optional[List[Post]]'


from app1.contracts import User as UserInterface
from app1.contracts import Contact as ContactInterface
from app1.contracts import Post as PostInterface


#from uvicore.auth.models.user import UserModel as AuthOverride
#AuthOverride = uvicore.ioc.make('uvicore.auth.models.user.User')


#class User(Model['User'], metaclass=ModelMetaclass):
#class UserModel(AuthOverride):
class UserModel(Model['UserModel'], metaclass=ModelMetaclass):
#class UserModel(Model['UserModel']):
#class UserModel(Model['UserModel'], metaclass=ModelMetaclass):
#class _User(Model, metaclass=ModelMetaclass):
    """Auth User Model"""

    # Database connection and table information
    __tableclass__ = table.Users

    id: Optional[int] = Field('id',
        primary=True,
        description='Users primary ID',
        sortable=True,
        searchable=True,
    )

    email: str = Field('email',
        description='Users email and username',
        required=True,
    )

    # One-To-One - User has ONE Contact
    info: 'Optional[UserInfo]' = Field(None,
        description='User Info Model',
        relation=HasOne('uvicore.auth.models.user_info.UserInfo', 'user_id'),
    )


    # CUSTOM ###################################################################

    app1_extra: Optional[str] = Field('app1_extra',
        description='Extra column on auth.users by app1',
        required=False,
    )

    # One-To-One - User has ONE Contact
    contact: Optional[Contact] = Field(None,
        description='Users Contact Model',

        #has_one=('app1.models.contact.Contact', 'user_id', 'id'),
        #relation=HasOne('app1.models.contact.Contact', 'user_id', 'id'),
        relation=HasOne('app1.models.contact.Contact', 'user_id'),
        #relation=HasOne('app1.models.contact.Contact'),
    )

    # One-To-Many (One User has Many Posts)
    posts: Optional[List[Post]] = Field(None,
        description="Users Posts Model",

        #has_many=('app1.models.post.Post', 'creator_id', 'id'),
        #relation=HasMany('app1.models.post.Post', 'creator_id', 'id')
        relation=HasMany('app1.models.post.Post', 'creator_id')
        #relation=HasMany('app1.models.post.Post')
    )

# IoC Class Instance
User: UserModel = uvicore.ioc.make('uvicore.auth.models.user.User', UserModel)
#class User(UserIoc, Model[UserModel]): pass



# Update forwrad refs (a work around to circular dependencies)
#User = uvicore.ioc.make('uvicore.auth.models.User')
#Contact.update_forward_refs()



from app1.models.contact import Contact
#Contact = uvicore.ioc.make('app1.models.contact.Contact')

from uvicore.auth.models.user_info import UserInfo
#from uvicore.auth.models.user_info import UserInfoModel as UserInfo
#UserInfo = uvicore.ioc.make('uvicore.auth.models.user_info.UserInfo')

from app1.models.post import Post
#Post = uvicore.ioc.make('app1.models.post.Post')


#UserModel.update_forward_refs()
User.update_forward_refs()
