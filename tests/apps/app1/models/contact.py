from __future__ import annotations


import uvicore
from app1.database.tables import contacts as table
#from uvicore.orm.fields import BelongsTo, Field
#from uvicore.orm.model import Model, ModelMetaclass
from uvicore.orm import Model, ModelMetaclass, Field, BelongsTo


# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from uvicore.auth.models.user import User


#from uvicore.auth.models.user import User
#User = uvicore.ioc.make('uvicore.auth.models.User')


#E = TypeVar("E", bound='_Contact')

#from app1.contracts import User as UserInterface
#from app1.models.user import User
#from uvicore.auth.models.user import User

#@uvicore.ioc.bind('app1.models.contact.Contact')

@uvicore.model()
class Contact(Model['Contact'], metaclass=ModelMetaclass):
#class ContactModel(Model['ContactModel'], metaclass=ModelMetaclass):
#class ContactModel(Model['ContactModel']):
#class _Contact2:
    """App1 Contacts"""

    # Databas        u.contact.e table definition
    __tableclass__ = table.Contacts

    id: int | None = Field('id',
        primary=True,
        description='Contact ID',
        #read_only=True,
    )

    name: str = Field('name',
        description='Contact Name (First and Last or Company)',
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
    )

    # One-To-One Inverse - Contact has ONE User
    user: 'User | None' = Field(None,
        description="Contact User Model",

        #belongs_to=('uvicore.auth.models.user.User', 'id', 'user_id'),
        #relation=BelongsTo('uvicore.auth.models.user.User', 'id', 'user_id')
        relation=BelongsTo('uvicore.auth.models.user.User')
    )


from app1.models.user import User  # isort:skip
#from uvicore.auth.models.user import User
#User = uvicore.ioc.make('uvicore.auth.models.user.User')
