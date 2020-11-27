from __future__ import annotations
import uvicore
from typing import Optional, List
from app1.database.tables import tags as table
from uvicore.orm.fields import Field, BelongsToMany, BelongsTo
from uvicore.orm.model import Model, ModelMetaclass

from app1.contracts import Tag as TagInterface

#@uvicore.ioc.bind('app1.models.tag.Tag')

@uvicore.model()
class Tag(Model['Tag'], metaclass=ModelMetaclass):
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

    creator_id: int = Field('creator_id',
        description="Tag Creator UserID",
        required=True,
    )

    # One-To-Many Inverse (One Post has One User)
    creator: Optional[User] = Field(None,
        description="Tag Creator User Model",

        #relation=BelongsTo('uvicore.auth.models.user.User', 'id', 'creator_id'),
        relation=BelongsTo('uvicore.auth.models.user.User'),
    )

    posts: Optional[List[Post]] = Field(None,
        description="Tag Posts Model",
        relation=BelongsToMany('app1.models.post.Post', join_tablename='post_tags', left_key='tag_id', right_key='post_id'),
    )



# IoC Class Instance
#Tag: TagModel = uvicore.ioc.make('app1.models.tag.Tag', TagModel)


from app1.models.user import User  # isort:skip
from app1.models.post import Post
Tag.update_forward_refs()

# class Tag(
#     uvicore.ioc.make('app1.models.tag.Tag'),
#     Model[_Tag],
#     TagInterface
# ): pass
