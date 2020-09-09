import uvicore
from typing import Optional
from uvicore.orm.model import Model
from uvicore.orm.fields import Field
from uvicore.auth.database.tables import users
from uvicore.support.dumper import dd, dump


class _User(Model):
    """Auth User Model"""

    # Database connection and table information
    __tableclass__ = users.Table

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
User: _User = uvicore.ioc.make('uvicore.auth.models.User')
