from __future__ import annotations
import uvicore
from uvicore.typing import Optional, Dict, Union, List
from uvicore.auth.support import password as pwd
from uvicore.support.dumper import dd, dump
from uvicore.auth.models import Group, Role
from uvicore.auth.database.tables import users as table
from uvicore.orm import Model, ModelMetaclass, Field, BelongsTo, BelongsToMany
from uvicore.auth import User as AuthUser
from uvicore.support.hash import sha1
from datetime import datetime


@uvicore.model()
class User(Model['User'], metaclass=ModelMetaclass):
    """Auth User Model"""

    # Database connection and table information
    __tableclass__ = table.Users

    id: Optional[int] = Field('id',
        primary=True,
        required=False,
        description='User Primary ID',
        sortable=True,
        searchable=True,
    )

    uuid: Optional[str] = Field('uuid',
        description='Custom Alternate UUID',
        required=False,
    )

    username: str = Field('username',
        description='User Login Username',
        required=True,
    )

    email: str = Field('email',
        description='User Email',
        required=True,
    )

    first_name: str = Field('first_name',
        description='User First Name',
        required=True,
    )

    last_name: str = Field('last_name',
        description='User Last Name',
        required=True,
    )

    title: Optional[str] = Field('title',
        description='User Title',
        required=False,
    )

    avatar_url: Optional[str] = Field('avatar_url',
        description='User Avatar URL',
        required=False,
    )

    password: Optional[str] = Field('password',
        description='User Last Name',
        required=False,
        read_only=False,
        write_only=True,
    )

    disabled: Optional[bool] = Field('disabled',
        description='User Disabled',
        required=False,
        default=False,
    )

    creator_id: int = Field('creator_id',
        description="User Creator UserID",
        required=True,
    )

    # One-To-Many Inverse (One Post has One Creator)
    creator: Optional[User] = Field(None,
        description="Post Creator User Model",
        #relation=BelongsTo('uvicore.auth.models.user.User', 'id', 'creator_id'),
        relation=BelongsTo('uvicore.auth.models.user.User'),
    )

    created_at: Optional[datetime] = Field('created_at',
        description='Created at Datetime',
        required=False,
        read_only=True,
    )

    updated_at: Optional[datetime] = Field('updated_at',
        description='Updated at Datetime',
        required=False,
        read_only=True,
    )

    login_at: Optional[datetime] = Field('login_at',
        description='Last Login Datetime',
        required=False,
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
