import jwt
import uvicore
from uvicore.auth.user import User
from uvicore.support.hash import sha1
from uvicore.contracts import UserProvider
from uvicore.support.dumper import dump, dd
from uvicore.http.request import HTTPConnection
from uvicore.auth.support import password as pwd
from uvicore.typing import List, Union, Any, Dict, Optional, Callable
from uvicore.support import module


@uvicore.service()
class Jwt(UserProvider):
    """Retrieve user from JWT header during Authentication middleware

    This is a stateless, databaseless authenticator using contents from the JWT only!
    """

    async def _retrieve_user(self,
        key_name: str,
        key_value: Any,
        request: HTTPConnection,
        *,

        # Parameters from auth config
        anonymous: bool = False,
        anonymous_user: Dict = {},
        jwt_mapping: Dict = {},

        # Parameters from authenticator method
        jwt: Dict = {},
        role_permission_mapper: Optional[Callable] = None,

        # Must have kwargs for infinite allowed optional params, even if not used.
        **kwargs,
    ) -> User:

        if anonymous:
            # User is not logged in.
            # New anonymous user based on anonymous user configuration
            anonymous_user['authenticated'] = False
            user = User(**anonymous_user)

        else:
            # New user based on JWT and mappings configuration
            user = User(
                id=jwt_mapping.id(jwt) or jwt.sub or 'Unknown',
                uuid=jwt_mapping.uuid(jwt) or jwt.sub or 'Unknown',
                username=jwt_mapping.email(jwt) or jwt.email or 'Unknown',
                email=jwt_mapping.email(jwt) or jwt.email or 'Unknown',
                first_name=jwt_mapping.first_name(jwt) or jwt.first_name or '',
                last_name=jwt_mapping.last_name(jwt) or jwt.last_name or '',
                title=jwt_mapping.title(jwt) or jwt.title or '',
                avatar=jwt_mapping.avatar(jwt) or jwt.avatar or '',
                groups=jwt_mapping.groups(jwt) or jwt.groups or [],
                roles=jwt_mapping.roles(jwt) or jwt.roles or [],
                permissions=jwt_mapping.permissions(jwt) or jwt.permissions or [],
                superadmin=jwt_mapping.superadmin(jwt) or jwt.admin or False,
                authenticated=True,
            )

        # If a role_permission_mapper callable is passed, call it to map
        # JWT roles to static hard coded permissions for stateless scopes
        if role_permission_mapper is not None:
            # Import mapper passing in user object
            mapper = module.load(role_permission_mapper).object()

            # Call __call__ on mapper
            user.permissions = await mapper(user)

        # Return user
        return user

    # async def retrieve_by_id(self, id: Union[str, int], request: HTTPConnection, **kwargs) -> User:
    #     """Retrieve user by primary key from the user provider backend.  No validation."""
    #     return await self._retrieve_user('id', id, request, **kwargs)

    # async def retrieve_by_uuid(self, uuid: str, request: HTTPConnection, **kwargs) -> User:
    #     """Retrieve the user by uuid from the user provider backend.  No validation."""
    #     return await self._retrieve_user('uuid', uuid, request, **kwargs)

    # async def retrieve_by_username(self, username: str, request: HTTPConnection, **kwargs) -> User:
    #     """Retrieve the user by username from the user provider backend.  No validation."""
    #     return await self._retrieve_user('email', username, request, **kwargs)

    # async def retrieve_by_credentials(self, username: str, password: str, request: HTTPConnection, **kwargs) -> User:
    #     """Retrieve the user by username from the user provider backend AND validate the password if not None"""
    #     return await self._retrieve_user('email', username, request, password=password, **kwargs)


