import jwt
import uvicore
from uvicore.auth.user_info import UserInfo
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
        role_permission_map: Optional[Dict] = None,

        # Must have kwargs for infinite allowed optional params, even if not used.
        **kwargs,
    ) -> UserInfo:
        """Retrieve user from backend"""

        if anonymous:
            # User is not logged in.
            # New anonymous user based on anonymous user configuration
            user = UserInfo(**anonymous_user)
            user.authenticated = False

        else:
            # New user based on JWT and mappings configuration
            user = UserInfo(
                id=jwt_mapping.id(jwt) or jwt.sub or 'Unknown',
                uuid=jwt_mapping.uuid(jwt) or jwt.sub or 'Unknown',
                sub=jwt_mapping.uuid(jwt) or jwt.sub or 'Unknown',
                username=jwt_mapping.username(jwt) or jwt.email or 'Unknown',
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

        # If a role_permission_map Dict is passed, map user 'roles' into user
        # permissions for stateless scopes
        if role_permission_map is not None:
            # Import mapper passing in user object
            #mapper = module.load(role_permission_mapper).object()

            # Call __call__ on mapper
            #user.permissions = await mapper(user)

            permissions = []
            for role in user.roles:
                if role in role_permission_map:
                    permissions.extend(role_permission_map[role])
            user.permissions = permissions

        # Return user
        return user
