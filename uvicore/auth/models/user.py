from __future__ import annotations
import uvicore
from uvicore.typing import Optional, Dict, Union
from uvicore.auth.support import password as pwd
from uvicore.support.dumper import dd, dump
from uvicore.auth.models import Group, Role
from uvicore.auth.database.tables import users as table
from uvicore.orm import Model, ModelMetaclass, Field, BelongsTo, BelongsToMany
from uvicore.auth import UserInfo


@uvicore.model()
class User(Model['User'], metaclass=ModelMetaclass):
    """Auth User Model"""

    # Database connection and table information
    __tableclass__ = table.Users

    id: Optional[int] = Field('id',
        primary=True,
        description='User Primary ID',
        sortable=True,
        searchable=True,
    )

    uuid: Optional[str] = Field('uuid',
        description='Custom Alternate UUID',
        required=False,
    )

    email: str = Field('email',
        description='User Email and Username',
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

    @classmethod
    async def userinfo(entity, provider: Dict, id: int = None, username: str = None, password: str = None) -> UserInfo:
        """Build Auth User Info Object and optionally validate password if provided"""

        # Check if user already validated in cache
        cache_key = 'auth/userinfo/' + username
        if await uvicore.cache.has(cache_key):
            dump('FROM CACHE')
            # Retrieve user from cache, no password check required
            userinfo = await uvicore.cache.get(cache_key)
            #dump(userinfo)
            return userinfo

        else:
            dump('FROM DB')
            # Cache not found.  Query user, validate password and convert to userinfo object
            # Do NOT utilize ORM cache, we handle here manually

            # Find based on ID or email
            kwargs = {entity.pk: id} if id else {'email': username}

            # Get includes from auth config
            includes = provider.includes

            user = await (entity.query()
                .include(*includes)
                #.where('disabled', False) # Throws Warning: Truncated incorrect DOUBLE value: '=', even with 0 or 1, string fixes it
                .where('disabled', '0')
                .show_writeonly(['password'])
                .find(**kwargs)
            )
            # User not found or disabled.  Return None means not verified or found.
            if not user: return None

            # If password, validate
            if password is not None:
                if not pwd.verify(password, user.password):
                    # Invalid password.  Return None means not verified or found.
                    return None

            # Build result SuperDict
            userinfo = UserInfo()
            userinfo.id = user.id
            userinfo.uuid = user.uuid
            userinfo.email = user.email
            userinfo.first_name = user.first_name
            userinfo.last_name = user.last_name
            userinfo.title = user.title
            userinfo.avatar_url = user.avatar_url

            # Get users groups->roles->permissions (roles linked to a group)
            groups = []
            roles = []
            permissions = []
            if 'groups' in includes:
                user_groups = user.groups
                if user_groups:
                    for group in user_groups:
                        groups.append(group.name)
                        if not group.roles: continue
                        for role in group.roles:
                            roles.append(role.name)
                            if not role.permissions: continue
                            for permission in role.permissions:
                                permissions.append(permission.name)

            # Get users roles->permissions (roles linked directly to the user)
            if 'roles' in includes:
                user_roles = user.roles
                if user_roles:
                    for role in user_roles:
                        roles.append(role.name)
                        if not role.permissions: continue
                        for permission in role.permissions:
                            permissions.append(permission.name)

            # Unique groups, roles and permissions (sets are unique)
            userinfo.groups = list(set(groups))
            userinfo.roles = list(set(roles))
            userinfo.permissions = list(set(permissions))

            # Set super admin, existence of 'admin' permission
            userinfo.superadmin = False
            if 'admin' in userinfo.permissions:
                # No need for any permissinos besides ['admin']
                userinfo.permissions = ['admin']
                userinfo.superadmin = True

            # Save to cache
            await uvicore.cache.put(cache_key, userinfo, seconds=10)
            #dump(userinfo)
            return userinfo

    async def _before_save(self) -> None:
        """Hook fired before record is saved (inserted or updated)"""
        await super()._before_save()

        # Convert password to hash if is plain text (works for first insert and updates)
        if self.password is not None and 'argon2' not in self.password:
            self.password = pwd.create(self.password)
