from __future__ import annotations
import uvicore
from uvicore.typing import Optional, List
from uvicore.auth.models.role import Role
from uvicore.support.dumper import dd, dump
from uvicore.orm import Model, ModelMetaclass, Field, BelongsToMany
from uvicore.auth.database.tables import groups as table


@uvicore.model()
class Group(Model['Group'], metaclass=ModelMetaclass):
    """Auth Group Model"""

    __tableclass__ = table.Groups

    id: Optional[int] = Field('id',
        primary=True,
        description='Group ID',
    )

    # key: str = Field('key',
    #     primary=True,
    #     description='Group Primary Key',
    # )

    name: str = Field('name',
        description='Group Name',
    )

    # Many-To-Many via group_roles pivot table
    roles: Optional[List[Role]] = Field(None,
        description="Group Roles",
        relation=BelongsToMany('uvicore.auth.models.role.Role', join_tablename='group_roles', left_key='group_id', right_key='role_id'),
    )
