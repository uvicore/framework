from __future__ import annotations

import uvicore
from typing import Optional
from uvicore.auth.models.user import User
from uvicore.support.dumper import dd, dump
from uvicore.orm import Model, ModelMetaclass, BelongsTo, Field
from xx_vendor.xx_appname.database.tables import xx_tablename as table


@uvicore.model()
class xx_ModelName(Model['xx_ModelName'], metaclass=ModelMetaclass):
    """xx_AppName xx_ModelName Model"""

    # Database table definition
    __tableclass__ = table.xx_TableName

    id: Optional[int] = Field('id',
        primary=True,
        description='Post ID',
        #sortable=True,
        #searchable=True,
        read_only=True,
    )

    slug: str = Field('slug',
        description='URL Friendly Post Title Slug',
        required=True,
    )

    title: str = Field('title',
        description='Post Title',
        required=True,
    )
