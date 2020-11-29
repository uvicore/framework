from __future__ import annotations

from typing import Optional

import uvicore
from uvicore.auth.database.tables import groups as table
#from uvicore.orm.fields import Field
#from uvicore.orm.metaclass import ModelMetaclass
#from uvicore.orm.model import Model
from uvicore.support.dumper import dd, dump

from uvicore.orm import Model, ModelMetaclass, Field

@uvicore.model()
class Group(Model['Group'], metaclass=ModelMetaclass):
    """Auth Group Model"""

    # Database connection and table information
    __tableclass__ = table.Groups

    id: Optional[int] = Field('id',
        primary=True,
        description='Group primary ID',
        sortable=True,
        searchable=True,
    )

    name: str = Field('name',
        description='Group Name',
        required=True,
    )

# IoC Class Instance
#Group: GroupModel = uvicore.ioc.make('uvicore.auth.models.group.Group', GroupModel)

# class Group(
#     _Group,
#     Model[_Group],
#     GroupInterface
# ): pass
