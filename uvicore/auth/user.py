import uvicore
from uvicore.typing import List, Union
from uvicore.contracts import User as UserInterface
from uvicore.contracts import UserProvider
from uvicore.support.dumper import dump, dd
from uvicore.support.hash import sha1
from uvicore.auth.support import password as pwd


@uvicore.service()
class User(UserInterface):
    """Auth logged in user dataclass representation"""

    @property
    def name(self):
        """First and last name"""
        return str(self.first_name + ' ' + self.last_name).strip()

    @property
    def avatar_url(self):
        """Alias to avatar"""
        return self.avatar

    @property
    def admin(self):
        """Alias to superadmin"""
        return self.superadmin

    @property
    def is_admin(self):
        """Alias to superadmin"""
        return self.superadmin

    @property
    def is_superadmin(self):
        """Alias to superadmin"""
        return self.superadmin

    @property
    def is_authenticated(self):
        """Alias to authenticated"""
        return self.authenticated

    @property
    def loggedin(self):
        """Alias to authenticated"""
        return self.authenticated

    @property
    def is_loggedin(self):
        """Alias to authenticated"""
        return self.authenticated

    @property
    def check(self):
        """Alias to authenticated"""
        return self.authenticated

    def can(self, permissions: Union[str, List]) -> bool:
        """Check if user has ALL of these permissions"""
        if self.superadmin: return True

        permissions = [permissions] if isinstance(permissions, str) else permissions

        for permission in permissions:
            if permission not in self.permissions:
                return False
        return True

    def can_any(self, permissions: Union[str, List]) -> bool:
        """Check if user has any one of these permissions"""
        if self.superadmin: return True

        permissions = [permissions] if isinstance(permissions, str) else permissions

        for permission in permissions:
            if permission in self.permissions:
                return True
        return False

    def cant(self, permissions: Union[str, List]) -> bool:
        """Check if user does not have one of these permissions"""
        return not self.can(permissions)

    def cannot(self, permissions: Union[str, List]) -> bool:
        """Alias to cant"""
        return not self.cant(permissions)


@uvicore.service()
class UserProvider(UserProvider):
    """Responsible for querying and authenticating a user and tranlsating into our auth user dataclass"""

    async def retrieve_user(self, key_name, key_value, *, password: str = None, includes: List = None) -> User:
        # Import user here, not at script level
        from uvicore.auth.models.user import User as Model

        # Get password hash for cache key.  Password is still required to pull the right cache key
        # or else someone could login with an invalid password for the duration of the cache
        password_hash = '/' + sha1(password) if password is not None else ''
        if password is not None: password_hash = sha1(password)

        # Check if user already validated in cache
        cache_key = 'auth/user/' + str(key_value) + password_hash
        if await uvicore.cache.has(cache_key):
            # User is already validated and cached
            # Retrieve user from cache, no password check required because cache key has password has in it
            user = await uvicore.cache.get(cache_key)
            return user

        # Cache not found.  Query user, validate password and convert to user class
        kwargs = {key_name: key_value}
        db_user = await (Model.query()
            .include(*includes)
            #.where('disabled', False) # Throws Warning: Truncated incorrect DOUBLE value: '=', even with 0 or 1, string fixes it
            .where('disabled', '0')
            .show_writeonly(['password'])
            .find(**kwargs)
        )

        # User not found or disabled.  Return None means not verified or found.
        if not db_user: return None

        # If password, validate credentials
        if password is not None:
            if not pwd.verify(password, db_user.password):
                # Invalid password.  Return None means not verified or found.
                return None

        # Get users groups->roles->permissions (roles linked to a group)
        groups = []
        roles = []
        permissions = []
        if 'groups' in includes:
            user_groups = db_user.groups
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
            user_roles = db_user.roles
            if user_roles:
                for role in user_roles:
                    roles.append(role.name)
                    if not role.permissions: continue
                    for permission in role.permissions:
                        permissions.append(permission.name)

        # Unique groups, roles and permissions (sets are unique)
        groups = sorted(list(set(groups)))
        roles = sorted(list(set(roles)))
        permissions = sorted(list(set(permissions)))

        # Set super admin, existence of 'admin' permission
        superadmin = False
        if 'admin' in permissions:
            # No need for any permissinos besides ['admin']
            permissions = ['admin']
            superadmin = True

        # Build UserInfo dataclass with REQUIRED fields
        authenticated = True
        user = User(
            db_user.id,
            db_user.uuid,
            db_user.email,
            db_user.email,
            db_user.first_name,
            db_user.last_name,
            db_user.title,
            db_user.avatar_url,
            groups,
            roles,
            permissions,
            superadmin,
            authenticated,
        )

        # Save to cache
        await uvicore.cache.put(cache_key, user, seconds=10)
        return user

    async def retrieve_by_id(self, id: Union[str, int], *, includes: List = None) -> User:
        return await self.retrieve_user('id', id, includes=includes)

    async def retrieve_by_uuid(self, uuid: str, *, includes: List = None) -> User:
        return await self.retrieve_user('uuid', uuid, includes=includes)

    async def retrieve_by_username(self, username: str, *, includes: List = None) -> User:
        return await self.retrieve_user('email', username, includes=includes)

    async def retrieve_by_credentials(self, username: str, password: str, *, includes: List = None) -> User:
        return await self.retrieve_user('email', username, password=password, includes=includes)

