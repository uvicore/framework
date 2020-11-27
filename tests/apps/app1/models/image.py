from __future__ import annotations
import uvicore
from typing import Optional, Any
from app1.database.tables import images as table
from uvicore.orm.fields import Field
from uvicore.orm.model import Model, ModelMetaclass


#@uvicore.ioc.bind('app1.models.image.Image')

@uvicore.model()
class Image(Model['Image'], metaclass=ModelMetaclass):
    """App1 Polymorphic One-To-One Image"""

    # Database table definition
    __tableclass__ = table.Images

    id: Optional[int] = Field('id',
        primary=True,
        description='Image ID',
        read_only=True,
    )

    imageable_type: str = Field('imageable_type',
        description='Polymorphic Image Type',
        required=True,
    )

    imageable_id: int = Field('imageable_id',
        description="Polymorphic Image Type ID",
        required=True,
    )

    filename: str = Field('filename',
        description='Image filename (no path)',
        required=True,
    )

    size: int = Field('size',
        description="Image size (in bytes)",
        required=True,
    )

    # Polymorphic One-To-One dynamic model based on imageable_type and imageable_id
    # I never coded this inverse relation.  This would be more difficult as joins wouldn't work
    # I would have to query each distinct _type, then query each of those tables perhaps, unsure, but lots
    # of work.  The inverse isn't so important to me yet.
    # imageable: Optional[Any] = Field(None,
    #     description="Polymorphic Imageable Model",
    #     relation=MorphTo()
    # )


    # # One-To-Many Inverse (One Comment has One Post)
    # post: 'Optional[Post]' = Field(None,
    #     description="Comment Post Model",

    #     #belongs_to=('app1.models.post.Post', 'id', 'post_id'),
    #     #relation=BelongsTo('app1.models.post.Post', 'id', 'post_id'),
    #     relation=BelongsTo('app1.models.post.Post'),
    # )

    # creator_id: int = Field('creator_id',
    #     description="Comment Creator UserID",
    #     required=True,
    # )

    # # One-To-Many Inverse (One Post has One Creator)
    # creator: Optional[User] = Field(None,
    #     description="Comment Creator User Model",
    #     #relation=BelongsTo('uvicore.auth.models.user.User', 'id', 'creator_id'),
    #     relation=BelongsTo('uvicore.auth.models.user.User'),
    # )


# IoC Class Instance
#Image: ImageModel = uvicore.ioc.make('app1.models.image.Image', ImageModel)

# Update forwrad refs (a work around to circular dependencies)
#from app1.models.post import Post  # isort:skip
#from app1.models.user import User  # isort:skip
#Image.update_forward_refs()
