from __future__ import annotations
import uvicore
from typing import Optional, TypeVar
from app1.database.tables import contacts as table
from uvicore.orm.fields import Field, BelongsTo
from uvicore.orm.metaclass import ModelMetaclass
from uvicore.orm.model import Model

# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from uvicore.auth.models.user import User


#from uvicore.auth.models.user import User
#User = uvicore.ioc.make('uvicore.auth.models.User')


#E = TypeVar("E", bound='_Contact')

class ContactModel(Model, metaclass=ModelMetaclass):
#class ContactModel(Model['ContactModel']):
#class _Contact2:
    """App1 Contacts"""

    # Database table definition
    __tableclass__ = table.Contacts

    id: Optional[int] = Field('id',
        primary=True,
        description='Contact ID',
        #read_only=True,
    )

    name: str = Field('name',
        description='Contact Name (First and Last or Company)',
        required=True,
    )

    title: str = Field('title',
        description='Contact Title or Position',
    )

    address: str = Field('address',
        description='Contact Address',
    )

    phone: str = Field('phone',
        description='Contact Phone Number',
    )

    user_id: int = Field('user_id',
        description="Contacts User ID",
        required=True,
    )

    # One-To-One Inverse - Contact has ONE User
    user: 'Optional[User]' = Field(None,
        description="Contact User Model",

        #belongs_to=('uvicore.auth.models.user.User', 'id', 'user_id'),
        #relation=BelongsTo('uvicore.auth.models.user.User', 'id', 'user_id')
        relation=BelongsTo('uvicore.auth.models.user.User')

    )

# class _Contact(_Contact2, _Model[_Contact2], metaclass=ModelMetaclass):
#     pass


# IoC Class Instance
Contact: ContactModel = uvicore.ioc.make('app1.models.contact.Contact', ContactModel)

# Update forwrad refs (a work around to circular dependencies)
from app1.models.user import User
Contact.update_forward_refs()





#x = _Contact.find2(12)








# y = _Contact()