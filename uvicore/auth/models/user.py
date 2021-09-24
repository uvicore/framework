from __future__ import annotations
import uvicore
from uvicore.typing import Optional, Dict, Union, List
from uvicore.auth.support import password as pwd
from uvicore.support.dumper import dd, dump
from uvicore.auth.models import Group, Role
from uvicore.auth.database.tables import users as table
from uvicore.orm import Model, ModelMetaclass, Field, BelongsTo, BelongsToMany
from uvicore.support.hash import sha1
from datetime import datetime


@uvicore.model()
class User(Model['User'], metaclass=ModelMetaclass):
    """Auth User Model"""

    # Database connection and table information
    __tableclass__ = table.Users

    id: Optional[int] = Field('id',
        primary=True,
        description='User Primary ID',
        #sortable=True,
        #searchable=True,
    )

    uuid: Optional[str] = Field('uuid',
        description='Custom Alternate UUID',
    )

    username: str = Field('username',
        description='User Login Username',
    )

    email: str = Field('email',
        description='User Email',
    )

    first_name: str = Field('first_name',
        description='User First Name',
    )

    last_name: str = Field('last_name',
        description='User Last Name',
    )

    title: Optional[str] = Field('title',
        description='User Title',
    )

    avatar_url: Optional[str] = Field('avatar_url',
        description='User Avatar URL',
    )

    password: Optional[str] = Field('password',
        description='User Last Name',
        read_only=False,
        write_only=True,
    )

    disabled: Optional[bool] = Field('disabled',
        description='User Disabled',
        default=False,
    )

    creator_id: int = Field('creator_id',
        description="User Creator UserID",
    )

    # One-To-Many Inverse (One Post has One Creator)
    creator: Optional[User] = Field(None,
        description="Post Creator User Model",
        #relation=BelongsTo('uvicore.auth.models.user.User', 'id', 'creator_id'),
        relation=BelongsTo('uvicore.auth.models.user.User'),
    )

    created_at: Optional[datetime] = Field('created_at',
        description='Created at Datetime',
        read_only=True,
    )

    updated_at: Optional[datetime] = Field('updated_at',
        description='Updated at Datetime',
        read_only=True,
    )

    login_at: Optional[datetime] = Field('login_at',
        description='Last Login Datetime',
    )

    # Many-To-Many via user_groups pivot table
    groups: Optional[List[Group]] = Field(None,
        description="User Groups",
        relation=BelongsToMany('uvicore.auth.models.group.Group', join_tablename='user_groups', left_key='user_id', right_key='group_id'),
    )

    # Many-To-Many via user_groups pivot table
    roles: Optional[List[Role]] = Field(None,
        description="User Roles",
        relation=BelongsToMany('uvicore.auth.models.role.Role', join_tablename='user_roles', left_key='user_id', right_key='role_id'),
    )

    async def _before_save(self) -> None:
        """Hook fired before record is saved (inserted or updated)"""
        await super()._before_save()

        # Convert password to hash if is plain text (works for first insert and updates)
        if self.password is not None and 'argon2' not in self.password:
            self.password = pwd.create(self.password)


# Required because I reference myself (creator_id)
User.update_forward_refs()
