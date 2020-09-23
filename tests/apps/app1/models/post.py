from __future__ import annotations
import uvicore
from typing import Optional, List
from app1.database.tables import posts as table
from uvicore.orm.fields import Field, HasMany, BelongsTo
from uvicore.orm.metaclass import ModelMetaclass, _ModelMetaclass
from uvicore.orm.model import Model


class PostModel(Model['PostModel'], metaclass=ModelMetaclass):
#class PostModel(Model['PostModel']):
    """App1 Posts"""

    # Database table definition
    __tableclass__ = table.Posts

    id: Optional[int] = Field('id',
        primary=True,
        description='Post ID',
        sortable=False,
        searchable=True,
        read_only=True,
        # properties={
        #     'test': 'hi'
        # }
    )

    slug: str = Field('unique_slug',
        description='URL Friendly Post Title Slug',
        required=True,
        # properties={
        #     'stuff': 'hi'
        # }
    )

    title: str = Field('title',
        description='Post Title',
        required=True,
    )

    other: str = Field('other',
        description='Post Other',
    )

    cb: str = Field(None,
        callback='cb_results'
    )

    creator_id: int = Field('creator_id',
        description="Post Creator UserID",
        required=True,
    )

    # One-To-Many Inverse (One Post has One User)
    creator: 'Optional[UserModel]' = Field(None,
        description="Post Creator User Model",

        #belongs_to=('uvicore.auth.models.user.User', 'id', 'creator_id'),
        #relation=BelongsTo('uvicore.auth.models.user.User', 'id', 'creator_id'),
        relation=BelongsTo('uvicore.auth.models.user.User'),
    )

    # One-To-Many (One Post has Many Comments)
    comments: 'Optional[List[CommentModel]]' = Field(None,
        description="Post Comments Model",

        #has_many=('app1.models.comment.Comment', 'post_id', 'id'),
        #relation=HasMany('app1.models.comment.Comment', 'post_id', 'id'),
        relation=HasMany('app1.models.comment.Comment', 'post_id'),
        #relation=HasMany('app1.models.comment.Comment'),
    )

    def cb_results(self):
        return str(self.slug) + ' callback'


# IoC Class Instance
Post: PostModel = uvicore.ioc.make('app1.models.post.Post', PostModel)


# Update forwrad refs (a work around to circular dependencies)
from app1.models.comment import CommentModel
from app1.models.user import UserModel
Post.update_forward_refs()

