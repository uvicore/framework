from __future__ import annotations
import uvicore
from typing import Optional
from uvicore.auth.database.tables import users as table
from uvicore.orm.fields import Field
from uvicore.orm.metaclass import ModelMetaclass
from uvicore.orm.model import Model
from uvicore.support.dumper import dd, dump


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

# UserModel for typehints only.  Import User for actual usage.
#class UserModel(Model, metaclass=ModelMetaclass):
class UserModel(Model['UserModel'], metaclass=ModelMetaclass):
#class UserModel(Model['UserModel']):
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

    # class Config:
    #     extra = 'ignore'
    #     arbitrary_types_allowed = True


# IoC Class Instance
User: UserModel = uvicore.ioc.make('uvicore.auth.models.user.User', UserModel)
