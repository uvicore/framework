from __future__ import annotations
import uvicore
from typing import Optional
from app1.database.tables import comments as table
from uvicore.orm.fields import Field, BelongsTo
from uvicore.orm.model import Model, ModelMetaclass

# # Make Many
# Field, BelongsTo, ModelMetaclass = uvicore.ioc.make('uvicore.orm', [
#     'fields.Field',
#     'Field.BelongsTo',
#     'ModelMetaclass'
# ])

from app1.contracts import Comment as CommentInterface


#@uvicore.ioc.bind('app1.models.comment.Comment')

@uvicore.model()
class Comment(Model['Comment'], metaclass=ModelMetaclass):
#class CommentModel(Model['CommentModel']):
    """App1 Post Comments"""

    # Database table definition
    __tableclass__ = table.Comments

    id: Optional[int] = Field('id',
        primary=True,
        description='Comment ID',
        sortable=True,
        searchable=True,
        read_only=True,
    )

    title: str = Field('title',
        description='Comment Title',
        required=True,
    )

    body: str = Field('body',
        description='Comment Body',
    )

    post_id: int = Field('post_id',
        description="Comment PostID",
        required=True,
    )

    # One-To-Many Inverse (One Comment has One Post)
    post: 'Optional[Post]' = Field(None,
        description="Comment Post Model",

        #belongs_to=('app1.models.post.Post', 'id', 'post_id'),
        #relation=BelongsTo('app1.models.post.Post', 'id', 'post_id'),
        relation=BelongsTo('app1.models.post.Post'),
    )

    creator_id: int = Field('creator_id',
        description="Comment Creator UserID",
        required=True,
    )

    # One-To-Many Inverse (One Post has One Creator)
    creator: Optional[User] = Field(None,
        description="Comment Creator User Model",
        #relation=BelongsTo('uvicore.auth.models.user.User', 'id', 'creator_id'),
        relation=BelongsTo('uvicore.auth.models.user.User'),
    )


    def cb_results(self):
        return self.slug + ' callback'


# IoC Class Instance
#Comment: CommentModel = uvicore.ioc.make('app1.models.comment.Comment', CommentModel)

# class Comment(
#     _Comment,
#     Model[_Comment],
#     CommentInterface
# ): pass

# Update forwrad refs (a work around to circular dependencies)

from app1.models.post import Post  # isort:skip
from app1.models.user import User  # isort:skip
#Post = uvicore.ioc.make('app1.models.post.Post')
Comment.update_forward_refs()
#_Comment.update_forward_refs()
