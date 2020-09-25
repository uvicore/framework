from __future__ import annotations
import uvicore
from typing import Optional, List
from uvicore.auth.database.tables import users as table
from uvicore.orm.fields import Field, HasOne, HasMany
from uvicore.orm.metaclass import ModelMetaclass
from uvicore.orm.model import Model
from uvicore.support.dumper import dd, dump

#from typing import TYPE_CHECKING
#if TYPE_CHECKING:
#from app1.models.contact import Contact

#from app1.models.contact import Contact
#from app1.models import contact
#Contact = uvicore.ioc.make('app1.models.Contact')

# I am extending, no need to redefine columns twice
from uvicore.auth.models.user import UserModel as AuthOverride

# This is an override.  Do not import this Model, instead import
# the original in uvicore.auth.models
class UserModel(AuthOverride):
#class UserModel(Model['UserModel']):
#class UserModel(Model['UserModel'], metaclass=ModelMetaclass):
#class _User(Model, metaclass=ModelMetaclass):
    """Auth User Model"""

    # Database connection and table information
    __tableclass__ = table.Users

    # id: Optional[int] = Field('id',
    #     primary=True,
    #     description='Users primary ID',
    #     sortable=True,
    #     searchable=True,
    # )

    # email: str = Field('email',
    #     description='Users email and username',
    #     required=True,
    # )

    app1_extra: Optional[str] = Field('app1_extra',
        description='Extra column on auth.users by app1',
        required=False,
    )

    # One-To-One - User has ONE Contact
    contact: 'Optional[ContactModel]' = Field(None,
        description='Users Contact Model',

        #has_one=('app1.models.contact.Contact', 'user_id', 'id'),
        #relation=HasOne('app1.models.contact.Contact', 'user_id', 'id'),
        relation=HasOne('app1.models.contact.Contact', 'user_id'),
        #relation=HasOne('app1.models.contact.Contact'),
    )

    # One-To-Many (One User has Many Posts)
    posts: 'Optional[List[PostModel]]' = Field(None,
        description="Users Posts Model",

        #has_many=('app1.models.post.Post', 'creator_id', 'id'),
        #relation=HasMany('app1.models.post.Post', 'creator_id', 'id')
        relation=HasMany('app1.models.post.Post', 'creator_id')
        #relation=HasMany('app1.models.post.Post')
    )


# IoC Class Instance
User: UserModel = uvicore.ioc.make('uvicore.auth.models.user.User', UserModel)


# Update forwrad refs (a work around to circular dependencies)
#User = uvicore.ioc.make('uvicore.auth.models.User')
#Contact.update_forward_refs()

#Contact = uvicore.ioc.make('app1.models.Contact')
from app1.models.contact import ContactModel
from app1.models.post import PostModel
UserModel.update_forward_refs()

