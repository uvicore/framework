from __future__ import annotations
import uvicore
from uvicore.typing import Optional, Dict, Union
from uvicore.auth.support import password as pwd
from uvicore.support.dumper import dd, dump
from uvicore.auth.models import Group
from uvicore.auth.database.tables import users as table
from uvicore.orm import Model, ModelMetaclass, Field, BelongsTo, BelongsToMany


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
    # No, decided against user roles.  User must be in a group and roles are only linked to a group
    # roles: Optional[List[Role]] = Field(None,
    #     description="User Roles",
    #     relation=BelongsToMany('uvicore.auth.models.role.Role', join_tablename='user_roles', left_key='user_id', right_key='role_id'),
    # )

    @classmethod
    async def authinfo(entity, *, id: int = None, email: str = None, password: str = None) -> Dict:
        """User Info and Validation for Auth Query"""
        if id:
            kwargs = {entity.pk: id}
        else:
            kwargs = {'email': email}

        # Get includes from auth config
        config = uvicore.config.app.auth
        includes = config.user_includes
        password_field = config.user_password_field

        # Get user
        user = await (entity.query()
            .include(*includes)
            .show_writeonly([password_field])
            #.cache('/authinfo/' + email)
            .cache(seconds=10)
            .find(**kwargs)
        )
        if not user: return None

        # If password, validate
        if password is not None:
            if not pwd.verify(password, getattr(user, password_field)):
                # Invalid password
                return None

        # Remove password field from results
        #user = await entity.query().include(*includes).find(**kwargs)
        setattr(user, password_field, None)

        # Build result SuperDict
        auth = Dict(user.dict())

        # Convert user into a nicer dictionary
        groups = []
        roles = []
        permissions = []
        if 'groups' in includes:
            user_groups = auth.pop('groups')
            if user_groups:
                for group in user_groups:
                    groups.append(group.name)
                    if not group.roles: continue
                    for role in group.roles:
                        roles.append(role.name)
                        if not role.permissions: continue
                        for permission in role.permissions:
                            permissions.append(permission.name)

        # Add as unique (sets are unique)
        auth.groups = list(set(groups))
        auth.roles = list(set(roles))
        auth.permissions = list(set(permissions))
        return auth

    async def _before_save(self) -> None:
        """Hook fired before record is saved (inserted or updated)"""
        await super()._before_save()

        # Convert password to hash if is plain text (works for first insert and updates)
        if self.password is not None and 'argon2' not in self.password:
            self.password = pwd.create(self.password)

