import uvicore
from typing import Optional
from uvicore.orm.model import Model
from uvicore.orm.field import Field
from uvicore.auth.database.tables import users
from uvicore.support.dumper import dd, dump


class User(Model):
    """Auth User Model"""

    # Already have a table
    __connection__ = users.table.connection
    __tablename__ = users.table.name
    __table__ = users.table.schema

    id: Optional[int] = Field('id',
        description='Users primary ID',
        sortable=True,
        searchable=True,
    )

    email: str = Field('email',
        description='Users email and username',
        required=True,
    )
