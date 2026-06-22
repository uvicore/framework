from __future__ import annotations
import uvicore
from uvicore.support.dumper import dd, dump
from uvicore.orm import Model, ModelMetaclass, Field
from uvicore.auth.database.tables import permissions as table


@uvicore.model()
class Permission(Model['Permission'], metaclass=ModelMetaclass):
    """Auth Permission Model"""

    __tableclass__ = table.Permissions

    id: int | None = Field('id',
        primary=True,
        description='Permission ID',
    )

    entity: str | None = Field('entity',
        description='Permission Entity',
    )

    name: str = Field('name',
        description='Permission Name',
    )
