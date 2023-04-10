from __future__ import annotations

import uvicore
from typing import Dict, List, Optional
#from uvicore.auth.models.user import User
from uvicore.support.dumper import dd, dump
from uvicore.orm import Model, ModelMetaclass, Field
from xx_vendor.xx_appname.database.tables import xx_tablename as table
from uvicore.orm.fields import BelongsTo, BelongsToMany, HasMany, HasOne, MorphOne, MorphMany, MorphToMany


# ------------------------------------------------------------------------------
# Uvicore Database Model Schematic
# This schematic is filled with examples, a suppliment to the docs.
# Pick the best example for your use case and modify as needed!
# ------------------------------------------------------------------------------



# --------------------------------------------------------------------------
# Example: How to override the main uvicore.auth user table
# --------------------------------------------------------------------------
# AuthOverride = uvicore.ioc.make('uvicore.auth.models.user.User_BASE')
# @uvicore.model()
# class User(AuthOverride, Model['User'], metaclass=ModelMetaclass):
#     # your custom user fields
#     pass



@uvicore.model()
class xx_ModelName(Model['xx_ModelName'], metaclass=ModelMetaclass):
    """xx_AppName xx_ModelName Model"""

    # Database table definition
    # Optional as some models have no database table
    __tableclass__ = table.xx_TableName

    id: Optional[int] = Field('id',
        primary=True,
        description='xx_ModelName ID',
        #sortable=True,
        #searchable=True,
        read_only=True,
    )

    slug: str = Field('slug',
        description='URL Friendly xx_ModelName Title Slug',
    )

    title: str = Field('title',
        description='xx_ModelName Title',
    )

    # created_at: Optional[datetime] = Field('created_at',
    #     description='xx_ModelName Created at Datetime',
    #     read_only=True,
    # )

    # deleted: Optional[bool] = Field('deleted',
    #     description='xx_ModelName Deleted',
    #     default=False,
    # )



    # --------------------------------------------------------------------------
    # Example: One-To-One (Post has one info row)
    # --------------------------------------------------------------------------
    # info: Optional[PostInfo] = Field(None,
    #     description='Post Info Model',
    #     relation=HasOne('xx_vendor.xx_appname.models.post_info.PostInfo', foreign_key='post_id'),
    # )
        # PostInfo model would have the one-to-one inverse (info has one post)
        # post_id: int = Field('post_id',
        #     description="Post ID",
        # )
        # post: Optional[Post] = Field(None,
        #     description="Post Model",
        #     relation=BelongsTo('xx_vendor.xx_appname.models.post.Post')
        # )



    # --------------------------------------------------------------------------
    # Example:  One-To-Many Inverse (One Post has One Creator)
    # --------------------------------------------------------------------------
    # creator_id: int = Field('creator_id',
    #     description="Post Creator UserID",
    # )
    # creator: Optional[User] = Field(None,
    #     description="Post Creator User Model",
    #     # No need to define foreign_key and local_key as they assume id and creator_id
    #     #relation=BelongsTo('uvicore.auth.models.user.User', foreign_key='id', local_key='creator_id'),
    #     relation=BelongsTo('uvicore.auth.models.user.User'),
    # )
        # User model would have one-to-many (user has many posts)
        # posts: Optional[List[Post]] = Field(None,
        #     description="Users Posts Model",
        #     relation=HasMany('xx_vendor.xx_appname.models.post.Post', foreign_key='creator_id')
        # )



    # --------------------------------------------------------------------------
    # Example: One-To-Many Inverse (One Post has One Format)
    # But using key instead of id, so we explicitly define
    # --------------------------------------------------------------------------
    # format_key: str = Field('format_key',
    #     description='Post Format Key',
    # )
    # format: Optional[Format] = Field(None,
    #     description='Post Format Model',
    #     read_only=True,
    #     relation=BelongsTo('xx_vendor.xx_appname.models.Format', foreign_key='key', local_key='format_key'),
    # )



    # --------------------------------------------------------------------------
    # Example: Many-To-Many via post_tags pivot table
    # --------------------------------------------------------------------------
    # tags: Optional[List[Tag]] = Field(None,
    #     description="Post Tags",
    #     relation=BelongsToMany('xx_vendor.xx_appname.models.tag.Tag', join_tablename='post_tags', left_key='post_id', right_key='tag_id'),
    # )



    # --------------------------------------------------------------------------
    # Example: Polymorphic One-To-One image
    # --------------------------------------------------------------------------
    # image: Optional[Image] = Field(None,
    #     description="Post Image",
    #     relation=MorphOne('xx_vendor.xx_appname.models.image.Image', polyfix='imageable')
    # )



    # --------------------------------------------------------------------------
    # Example: Polymorphic Many-To-Many Hashtags
    # --------------------------------------------------------------------------
    #hashtags: Optional[List[Hashtag]] = Field(None,
    #hashtags: Optional[List[str]] = Field(None,
        # description="Post Hashtags",
        # relation=MorphToMany(
        #     model='xx_vendor.xx_appname.models.hashtag.Hashtag',
        #     join_tablename='hashtaggables',
        #     polyfix='hashtaggable',
        #     right_key='hashtag_id',
        #     # Or as a list
        #     #dict_key='id',
        #     #dict_value='name',
        #     #list_value='name',
        # ),



    # --------------------------------------------------------------------------
    # Example: Polymorphic One-To-Many attributes
    # --------------------------------------------------------------------------
    # attributes: Optional[List[Attribute]] = Field(None,
    # #attributes: Optional[Dict] = Field(None,  # As plain dict with dict_key and dict_value
    #     description="Post Attributes",
    #     # As plain dict
    #     #relation=MorphMany('xx_vendor.xx_appname.models.attribute.Attribute', polyfix='attributable', dict_key='key', dict_value='value')

    #     # Or as model
    #     relation=MorphMany('xx_vendor.xx_appname.models.attribute.Attribute', polyfix='attributable')



    # --------------------------------------------------------------------------
    # Example: Callback which is run AFTER the model has been instantiated
    # so it has access to self.  Think if this like a computed property.
    # --------------------------------------------------------------------------
    # cb: str = Field(None,
    #     callback='cb_results'
    # )
    # def cb_results(self):
    #     return str(self.slug) + ' callback'



    # --------------------------------------------------------------------------
    # Example: Evaluation logic which is run BEFORE the model has been instantiated.
    # so it has access to the incomming data (row), but not to self.
    # --------------------------------------------------------------------------
    # name: str = Field(None,
    #     # Using a inline lambda
    #     evaluate=lambda row: row['data']['name'] if 'data' in row else row['name']

    #     # Using a separate function
    #     evaluate=set_name

    #     # Using a separate function with parameters
    #     evaluate=(set_name, 'Data')
    # )



    # --------------------------------------------------------------------------
    # Example: Hooks into the model lifecycle
    # --------------------------------------------------------------------------
    # async def _before_insert(self) -> None:
    #     """Hook fired before record is inserted (new records only)"""
    #     await super()._before_insert()

    # async def _after_insert(self) -> None:
    #     """Hook fired after record is inserted (new records only)"""
    #     await super()._after_insert()

    # async def _before_save(self) -> None:
    #     """Hook fired before record is saved (inserted or updated)"""
    #     await super()._before_save()

    #     # Example: Convert password to hash if is plain text (works for first insert and updates)
    #     from uvicore.auth.support import password as pwd
    #     if self.password is not None and 'argon2' not in self.password:
    #         self.password = pwd.create(self.password)

    # async def _after_save(self) -> None:
    #     """Hook fired after record is saved (inserted or updated)"""
    #     await super()._after_save()

    # async def _before_delete(self) -> None:
    #     """Hook fired before record is deleted"""
    #     await super()._before_delete()

    # async def _after_delete(self) -> None:
    #     """Hook fired after record is deleted"""
    #     await super()._after_delete()



# ------------------------------------------------------------------------------
# Example: If models relate to each other, solve circular dependencies
# by importing some at the bottom and using update_forward_refs()
# ------------------------------------------------------------------------------
# Update forward refs to circumvent circular dependencies
# from uvicore.auth.models.user import User  # isort:skip
# from xx_vendor.xx_appname.models.post_info import PostInfo  # isort:skip
# from xx_vendor.xx_appname.models.tags import Tags  # isort:skip
# xx_ModelName.update_forward_refs()
