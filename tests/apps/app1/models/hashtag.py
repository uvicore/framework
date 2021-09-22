from __future__ import annotations
import uvicore
from typing import Optional, List
from app1.database.tables import hashtags as table
from uvicore.orm import Model, ModelMetaclass, Field, BelongsTo, BelongsToMany


@uvicore.model()
class Hashtag(Model['Hashtag'], metaclass=ModelMetaclass):
    """App1 Hashtags"""

    # Database table definition
    __tableclass__ = table.Hashtags

    id: Optional[int] = Field('id',
        primary=True,
        description='Hashtag ID',
        #sortable=False,
        #searchable=True,
        read_only=True,
    )

    name: str = Field('name',
        description='Hashtag Name',
        required=True,
    )

    @staticmethod
    async def post2(entity: Hashtag):
        return entity
