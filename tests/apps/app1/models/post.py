from __future__ import annotations

from typing import List, Optional, Dict

import uvicore
from app1.database.tables import posts as table
#from uvicore.orm.fields import BelongsTo, BelongsToMany, Field, HasMany, MorphOne, MorphMany
#from uvicore.orm.model import Model, ModelMetaclass
from app1.models.image import Image
from app1.models.attribute import Attribute
from uvicore.support.dumper import dump, dd

from uvicore.orm import Model, ModelMetaclass, Field, BelongsTo, BelongsToMany, HasMany, MorphOne, MorphMany, MorphToMany

#@uvicore.ioc.bind('app1.models.post.Post')

@uvicore.model()
class Post(Model['Post'], metaclass=ModelMetaclass):
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
        relation=HasMany('app1.models.comment.Comment', foreign_key='post_id'),
        #relation=HasMany('app1.models.comment.Comment'),
    )

    # Many-To-Many via post_tags pivot table
    tags: Optional[List[Tag]] = Field(None,
        description="Post Tags",
        relation=BelongsToMany('app1.models.tag.Tag', join_tablename='post_tags', left_key='post_id', right_key='tag_id'),
    )

    # Polymorphic One-To-One image
    image: Optional[Image] = Field(None,
        description="Post Image",
        relation=MorphOne('app1.models.image.Image', polyfix='imageable')
    )

    # Polymorphic One-To-Many Attributes
    #attributes: Optional[List[Attribute]] = Field(None,
    attributes: Optional[Dict] = Field(None,
        description="Post Attributes",
        relation=MorphMany('app1.models.attribute.Attribute', polyfix='attributable', dict_key='key', dict_value='value')
        #relation=MorphMany('app1.models.attribute.Attribute', polyfix='attributable')
    )

    # Polymorphic Many-To-Many Hashtags
    hashtags: Optional[List[Tag]] = Field(None,
        description="Post Hashtags",
        relation=MorphToMany('app1.models.hashtag.Hashtag', join_tablename='hashtaggables', polyfix='hashtaggable', right_key='hashtag_id')
    )



    def cb_results(self):
        return str(self.slug) + ' callback'

    async def _before_save(self):
        await super()._before_save()
        #dump('yyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
        #if self.other is not None:
            #self.other = self.other + ' !!!!!!!!!!!!!!!!!!!'



# @uvicore.events.listen('app1.models.post.PostModel-BeforeSave')
# def _event_inserting(event, payload):
#     dump('HANDLER FOR ' + event.get('name'))
#     #pass
#     #dump("event inserting here")
#     #dump(payload.model.extra1)
#     #dump(payload)
#     if payload.model.other is not None:
#         payload.model.other = payload.model.other + ' !!!!!!!!!!!!!'
#     #     #dump(payload.model.other)
#     #     pass
#     #payload.model.extra1 = 'user5 extra111'

# # #uvicore.events.listen('app1-models-post-PostModel-events-Inserting', _event_inserting)


# @uvicore.events.listen('app1.models.post.PostModel-AfterSave')
# def _event_inserting(event, payload):
#     dump('HANDLER FOR ' + event.get('name'))




# IoC Class Instance
#Post: PostModel = uvicore.ioc.make('app1.models.post.Post', PostModel)
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
