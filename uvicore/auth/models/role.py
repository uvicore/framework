from __future__ import annotations
import uvicore
from uvicore.typing import Optional, List
from uvicore.support.dumper import dd, dump
from uvicore.auth.models.permission import Permission
from uvicore.auth.database.tables import roles as table
from uvicore.orm import Model, ModelMetaclass, Field, BelongsToMany


@uvicore.model()
class Role(Model['Role'], metaclass=ModelMetaclass):
    """Auth Role Model"""

    __tableclass__ = table.Roles

    id: Optional[int] = Field('id',
        primary=True,
        description='Role ID',
    )

    name: str = Field('name',
        description='Role Name',
    )

    # superadmin: bool = Field('superadmin',
    #     default=False,
    #     description="Role is SuperAdmin"
    # )

    # Many-To-Many via role_permissions pivot table
    permissions: Optional[List[Permission]] = Field(None,
        description="Role Permissions",
        relation=BelongsToMany('uvicore.auth.models.permission.Permission', join_tablename='role_permissions', left_key='role_id', right_key='permission_id'),
    )
