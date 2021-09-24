from __future__ import annotations
import uvicore
from uvicore.typing import Optional
from uvicore.support.dumper import dd, dump
from uvicore.orm import Model, ModelMetaclass, Field
from uvicore.auth.database.tables import permissions as table


@uvicore.model()
class Permission(Model['Permission'], metaclass=ModelMetaclass):
    """Auth Permission Model"""

    __tableclass__ = table.Permissions

    id: Optional[int] = Field('id',
        primary=True,
        description='Permission ID',
    )

    entity: Optional[str] = Field('entity',
        description='Permission Entity',
    )

    name: str = Field('name',
        description='Permission Name',
    )
