import uvicore
from uvicore.auth.user_info import UserInfo
from uvicore.support.hash import sha1
from uvicore.contracts import UserProvider
from uvicore.support.dumper import dump, dd
from uvicore.auth.support import password as pwd
from uvicore.http.request import HTTPConnection
from uvicore.typing import List, Union, Any, Dict
from uvicore.auth.models.user import User as UserModel
from uvicore.auth.models.group import Group
from datetime import datetime


@uvicore.service()
class Orm(UserProvider):
    """Retrieve and validate user from uvicore.auth ORM User model during Authentication middleware

    This is NOT a stateless user provider as it queries the user, groups, roles tables from a database.
    """

    # def __init__(self):
    #     # Only need for an __init__ override is to modify field mappings
    #     super().__init__()

    #     # Temp, until I add username to ORM model
    #     self.field_map['username'] = 'email'

    async def _retrieve_user(self,
        key_name: str,
        key_value: Any,
        request: HTTPConnection,
        *,
        password: str = None,

        # Parameters from auth config
        anonymous: bool = False,
        includes: List = None,

        # Must have kwargs for infinite allowed optional params, even if not used.
        **kwargs,
    ) -> UserInfo:
        """Retrieve user from backend"""

        # Cache store
        # Array store is much faster than redis and since this is called at the
        # middleware level on every request, we want it to be as performant as possible.
        # Set to None to use config default.
        cache_store = 'array'

        # Get password hash for cache key.  Password is still required to pull the right cache key
        # or else someone could login with an invalid password for the duration of the cache
        password_hash = '/' + sha1(password) if password is not None else ''

        # Check if user already validated in cache, if so, skip DB hits!
        # Don't do a cache.has() becuase cache.get() already does it
        # and because of the array store _expire() it's a bit expensive.
        # Eliminating the duplicate has() saved me about 1500 req/sec on wrk benchmark
        cache_key = 'auth/user/' + str(key_value) + password_hash
        user = await uvicore.cache.store(cache_store).get(cache_key)
        if user:
            # User is already validated and cached
            # Retrieve user from cache, no password check required because cache key has password has in it
            #dump('Cached authentication middleware User found, load from cache!')
            return user

        # Interesting.  With a heavy 'wrk' performance test you can see this hit
        # a dozen times on the first run.  Because of await, while caching is
        # trying to take place, many other request are comming in and processing.
        # We actually hit the DB a dozen times before the first request is cached.
        # This is why we do 'wrk' at least twice, to "warm up" the cache.  Also
        # with 'array` cache store and gunicorn, its actually one cache registery
        # per THREAD unlinke the shared redis backend which is just one cache.  So
        # with gunicorn and array caching you will see at least N cache misses.
        # But even still you see several more due to the concurrency of wrk and the
        # time it takes for await to set the cache.
        # dump('UNcached authentication middleware User, load from DB')

        # ORM is currently thworing a Warning: Truncated incorrect DOUBLE value: '='
        # when using actual bool as bit value.  So I convert to '1' or '0' strings instead
        disabled = '1' if anonymous else '0'

        # Cache not found.  Query user, validate password and convert to user class
        find_kwargs = {key_name: key_value}
        db_user = await (UserModel.query()
            .include(*includes)
            .where('disabled', disabled)
            #.show_writeonly(['password'])
            .show_writeonly(True)
            .find(**find_kwargs)
        )

        # User not found or disabled.  Return None means not verified or found.
        if not db_user: return None

        # If we are checking passwords and the db_user has NO password, user cannot be logged into
        if password is not None and db_user.password is None: return None

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
        # Fixme, there is a 'superadmin' field on the roles table.
        # If user is in any role with superadmin=True they are a superadmin
        superadmin = False
        if 'admin' in permissions:
            # No need for any permissinos besides ['admin']
            permissions = ['admin']
            superadmin = True

        # Build UserInfo dataclass with REQUIRED fields
        user = UserInfo(
            id=db_user.id or '',
            uuid=db_user.uuid or '',
            sub=db_user.uuid or '',
            username=db_user.username or '',
            email=db_user.email or '',
            first_name=db_user.first_name or '',
            last_name=db_user.last_name or '',
            title=db_user.title or '',
            avatar=db_user.avatar_url or '',
            groups=groups or [],
            roles=roles or [],
            permissions=permissions or [],
            superadmin=superadmin or False,
            authenticated=not anonymous,
        )

        # Save to cache
        if anonymous and cache_store == 'array':
            # If anonymous user, set cache to NEVER expire. Why?  Because
            # the anonymouse user will never change, no need to have it expire from cache.
            # This only works if cache store is 'array' because it will die when we kill
            # the program.  If cache store is 'redis', we want it to expire in case anyone
            # changes what the anonymous user in the DB looks like at some point.
            await uvicore.cache.store(cache_store).put(cache_key, user, seconds=0)
        else:
            # User is a valid user, cache it using configs default TTL expire
            # Or user is anonymous but cache_store is redis, we need to expire in redis.
            await uvicore.cache.store(cache_store).put(cache_key, user)

        # Return to user
        return user

    async def create_user(self, request: HTTPConnection, **kwargs):
        """Create new user in backend"""

        # Consistent kwargs come from our JWT auto_create_user_jwt_mapping config
        # uuid, username, email, first_name, last_name
        # title, avatar, creator_id, groups (array)

        # Pop groups from kwargs
        groups = kwargs.pop('groups')

        # Set other kwargs values
        kwargs['disabled'] = False
        kwargs['login_at'] = datetime.now()

        # Translate avatar
        kwargs['avatar_url'] = kwargs.pop('avatar')

        # Build user model
        user = UserModel(**kwargs)

        # Get actual groups in backend from groups array
        real_groups = await Group.query().where('name', 'in', groups).get()

        # Save user
        await user.save()

        # Link real_groups
        await user.link('groups', real_groups)

        # Return new backend user (not actual Auth user class)
        return user

    async def sync_user(self, request: HTTPConnection, **kwargs):
        """Sync user and group linkage to backend"""
        # Sync not only name changes, but also group linkage

        # Consistent kwargs come from our JWT auto_create_user_jwt_mapping config
        # uuid, username, email, first_name, last_name
        # title, avatar, creator_id, groups (array)

        # Get username
        username = kwargs['username']

        # Get actual backend user
        user = await UserModel.query().show_writeonly(['password']).include('groups').find(username=username)

        # If we have successfully logged in, we are not disabled
        user.disabled = False
        user.login_at = datetime.now()

        # Pop groups from kwargs
        groups = kwargs.pop('groups')

        # Remove other kwargs items
        del kwargs['creator_id']

        # Translate avatar
        kwargs['avatar_url'] = kwargs.pop('avatar')

        # Add all other kwargs to user
        for key, value in kwargs.items():
            setattr(user, key, value)

        # Save user record
        await user.save()

        # UNLINK any groups from DB that are not listed in groups JWT array
        if groups and user.groups:
            unlink_groups = []
            for g in user.groups:
                if g.name not in groups:
                    unlink_groups.append(g)
            if unlink_groups: await user.unlink('groups', unlink_groups)

        # LINK any groups in JWT that are not linked in DB
        if groups:
            # Get actual groups in backend from groups array
            real_groups = await Group.query().where('name', 'in', groups).get()
            real_group_names = [x.name for x in real_groups]

            # Convert users existing groups to list of names
            user_group_names = []
            if user.groups:
                user_group_names = [x.name for x in user.groups]

            link_groups = []
            for g in real_groups:
                if g.name not in user_group_names:
                    link_groups.append(g)
            if link_groups: await user.link('groups', link_groups)

        # Return new backend user (not actual Auth user class)
        return user
