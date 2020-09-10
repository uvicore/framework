from typing import Optional
from uvicore.orm.model import Model
from uvicore.orm.fields import Field
from app1.database.tables import posts
from uvicore.auth.models.user import User


from uvicore.orm.metaclass import ModelMetaclass

#class Post(Model):
class Post(Model, metaclass=ModelMetaclass):
    """App1 Posts"""

    # Database table definition
    __tableclass__ = posts.Table

    id: Optional[int] = Field('id',
        primary=True,
        description='Post ID',
        sortable=True,
        searchable=True,
        read_only=True,
    )

    slug: str = Field('unique_slug',
        description='URL Friendly Post Title Slug',
        required=True,
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

    creator: Optional[User] = Field(None,
        description="Post Creator User Model",
        # One To Many (Inverse, called many-to-one)
        # A post has ONE user
        # Default assumes foreign is 'id' and local is field+_id
        belongs_to=(User, 'id', 'creator_id'),
    )

    def cb_results(self):
        return self.slug + ' callback'
