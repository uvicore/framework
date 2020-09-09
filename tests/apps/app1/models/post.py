from typing import Optional
from uvicore.orm.model import Model
from uvicore.orm.fields import Field
from app1.database.tables import posts
from uvicore.auth.models.user import User


class Post(Model):
    """App1 Posts"""

    # Database table definition
    __tableclass__ = posts.Table

    id: Optional[int] = Field('id',
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

    creator_id: int = Field('creator_id',
        description="Post Creator UserID",
        required=True,
    )

    creator: Optional[User] = Field(None,
        description="Post Creator User Model",
        # ForeignKey or many-to-one
        # Default assumes foreign is 'id' and local is field + _id
        #has_one=(User),
        has_one=(User, 'id', 'creator_id'),
    )
