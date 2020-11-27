from __future__ import annotations

from typing import List, Optional

import uvicore
from uvicore.auth.database.tables import users as table
from uvicore.orm.fields import Field, HasMany, HasOne, MorphOne
from uvicore.orm.model import Model, ModelMetaclass
from uvicore.contracts import Model as ModelInterface
from uvicore.support.dumper import dd, dump
from app1.models.image import Image


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
#from app1.contracts import Contact as ContactInterface
#from app1.contracts import Post as PostInterface


#ORIG HERE
#from BASE.uvicore.auth.models.user import UserModel as AuthOverride



# import importlib
# import sys
# fullname = 'uvicore.auth.models.user'
# spec = importlib.util.spec_from_file_location(fullname, '/home/mreschke/Code/mreschke/python/uvicore/uvicore/uvicore/auth/models/user.py')
# mod = importlib.util.module_from_spec(spec)
# #x = sys.modules.get(fullname)
# sys.modules[fullname] = mod
# spec.loader.exec_module(mod)
# #sys.modules[fullname] = x
# dump(mod)




#from uvicore.auth.database.tables.users import Users
#dump('TABLE', Users)

# Pull original User model from IoC _BASE
AuthOverride = uvicore.ioc.make('uvicore.auth.models.user.User_BASE')

#@uvicore.ioc.bind('app1.models.user.User')
#class User(Model['User'], metaclass=ModelMetaclass):

@uvicore.model()
class User(AuthOverride, Model['User'], metaclass=ModelMetaclass):


#class UserModel(Model['UserModel'], metaclass=ModelMetaclass):
#class UserModel(Model['UserModel']):
#class UserModel(Model['UserModel'], metaclass=ModelMetaclass):
#class _User(Model, metaclass=ModelMetaclass):
    """Auth User Model"""

    # Database connection and table information
    __tableclass__ = table.Users

    # id: Optional[int] = Field('id',
    #     primary=True,
    #     description='User Primary ID',
    #     sortable=True,
    #     searchable=True,
    # )

    # email: str = Field('email',
    #     description='User Email and Username',
    #     required=True,
    # )

    # # One-To-One - User has ONE Contact
    # info: Optional[UserInfo] = Field(None,
    #     description='User Info Model',
    #     relation=HasOne('uvicore.auth.models.user_info.UserInfo', foreign_key='user_id'),
    # )


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
        relation=HasOne('app1.models.contact.Contact', foreign_key='user_id'),
        #relation=HasOne('app1.models.contact.Contact'),
    )

    # One-To-Many (One User has Many Posts)
    posts: Optional[List[Post]] = Field(None,
        description="Users Posts Model",

        #has_many=('app1.models.post.Post', 'creator_id', 'id'),
        #relation=HasMany('app1.models.post.Post', 'creator_id', 'id')
        relation=HasMany('app1.models.post.Post', foreign_key='creator_id')
        #relation=HasMany('app1.models.post.Post')
    )

    # Polymorphic One-To-One image
    image: Optional[Image] = Field(None,
        description="Post Image",
        relation=MorphOne('app1.models.image.Image', polyfix='imageable')
    )


# IoC Class Instance
#User = UserModel
#User: UserModel = uvicore.ioc.make('uvicore.auth.models.user.User', UserModel)
#User: UserModel = uvicore.ioc.make('uvicore.auth.models.user.User')
#class User(UserIoc, Model[UserModel], UserInterface): pass


# class User(
#     _User,
#     Model[UserModel],
#     UserInterface
# ): pass



# Update forwrad refs (a work around to circular dependencies)
#User = uvicore.ioc.make('uvicore.auth.models.User')
#Contact.update_forward_refs()



from app1.models.contact import Contact  # isort:skip
#Contact = uvicore.ioc.make('app1.models.contact.Contact')

from uvicore.auth.models.user_info import UserInfo  # isort:skip
#from uvicore.auth.models.user_info import UserInfoModel as UserInfo
#UserInfo = uvicore.ioc.make('uvicore.auth.models.user_info.UserInfo')

from app1.models.post import Post  # isort:skip
#Post = uvicore.ioc.make('app1.models.post.Post')


#User.update_forward_refs()
#UserModel.update_forward_refs()
