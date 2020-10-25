from __future__ import annotations

from typing import List, Optional

import uvicore
from app1.contracts import Post as PostInterface
from app1.database.tables import posts as table
from uvicore.orm.fields import BelongsTo, BelongsToMany, Field, HasMany
from uvicore.orm.model import Model, ModelMetaclass


class PostModel(Model['PostModel'], metaclass=ModelMetaclass):
#class _PostModel(Model['PostModel'], PostInterface, metaclass=ModelMetaclass):
#class _PostModel(Model['PostModel'], metaclass=ModelMetaclass):
#class PostModel(Model['PostModel'], ModelInterface['PostModel'], metaclass=ModelMetaclass):
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
        #     'stuff': 'hi',
        #     'stuff2': 'hi2',
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

    # One-To-Many Inverse (One Post has One Creator)
    creator: Optional[User] = Field(None,
        description="Post Creator User Model",
        #relation=BelongsTo('uvicore.auth.models.user.User', 'id', 'creator_id'),
        relation=BelongsTo('uvicore.auth.models.user.User'),
    )

    owner_id: int = Field('owner_id',
        description="Post Owner UserID",
        required=True,
    )

    # One-To-Many Inverse (One Post has One Owner)
    owner: Optional[User] = Field(None,
        description="Post Owner User Model",
        #relation=BelongsTo('uvicore.auth.models.user.User', 'id', 'owner_id'),
        relation=BelongsTo('uvicore.auth.models.user.User'),
    )

    # One-To-Many (One Post has Many Comments)
    comments: Optional[List[Comment]] = Field(None,
        description="Post Comments Model",

        #has_many=('app1.models.comment.Comment', 'post_id', 'id'),
        #relation=HasMany('app1.models.comment.Comment', 'post_id', 'id'),
        relation=HasMany('app1.models.comment.Comment', 'post_id'),
        #relation=HasMany('app1.models.comment.Comment'),
    )

    tags: Optional[List[Tag]] = Field(None,
        description="Post Tags",
        relation=BelongsToMany('app1.models.tag.Tag', 'post_tags', 'post_id', 'tag_id'),
    )

    def cb_results(self):
        return str(self.slug) + ' callback  asdfasdfasdf'

# IoC Class Instance
Post: PostModel = uvicore.ioc.make('app1.models.post.Post', PostModel)
#class Post(PostIoc, Model[PostModel], PostInterface): pass

# class Post(
#     _Post,
#     Model[PostModel],
#     PostInterface
# ): pass


# Update forwrad refs (a work around to circular dependencies)
# If the relation has an ID foreign key on this table, use ioc.make
# If not (the reverse relation) use from xyz import abc


#from uvicore.auth.models.user import User  # isort:skip
#from app1.models.user import User  # isort:skip
from app1.models.comment import Comment  # isort:skip
from app1.models.tag import Tag  # isort:skip

#from uvicore.auth.models.user import User  # isort:skip
from app1.models.user import User  # isort:skip
#User = uvicore.ioc.make('uvicore.auth.models.user.User')
#Comment = uvicore.ioc.make('app1.models.comment.Comment')
#Tag = uvicore.ioc.make('app1.models.tag.Tag')

Post.update_forward_refs()
#PostModel.update_forward_refs()
