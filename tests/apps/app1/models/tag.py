from __future__ import annotations
import uvicore
from typing import Optional, List
from app1.database.tables import tags as table
from uvicore.orm.fields import Field, HasMany, BelongsTo
from uvicore.orm.metaclass import ModelMetaclass
from uvicore.orm.model import Model

from app1.contracts import Tag as TagInterface

class TagModel(Model['TagModel'], metaclass=ModelMetaclass):
    """App1 Tags"""

    # Database table definition
    __tableclass__ = table.Tags

    id: Optional[int] = Field('id',
        primary=True,
        description='Post ID',
        sortable=False,
        searchable=True,
        read_only=True,
    )

    name: str = Field('name',
        description='Tag Name',
        required=True,
    )


# IoC Class Instance
Tag: TagModel = uvicore.ioc.make('app1.models.tag.Tag', TagModel)

# class Tag(
#     uvicore.ioc.make('app1.models.tag.Tag'),
#     Model[_Tag],
#     TagInterface
# ): pass
