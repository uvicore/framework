import uvicore
from uvicore.support import module
from uvicore.support.dumper import dump, dd
from uvicore.http.request import HTTPConnection
from uvicore.contracts import User, UserProvider
from uvicore.typing import Dict, Optional, List, Tuple
from uvicore.contracts import Authenticator as AuthenticatorInterface


@uvicore.service()
class Authenticator(AuthenticatorInterface):
    """Base authenticator class"""

    def __init__(self, config: Dict):
        self.config = config

    # This can probably be private _ ??
    async def retrieve_user(self, username: str, password: str, provider: Dict, request: HTTPConnection, **kwargs) -> Optional[User]:
        """Retrieve user from User Provider backend"""

        # Import user provider defined in auth config
        user_provider: UserProvider = module.load(provider.module).object()

        # Get user from user provider and validate password
        # If returned user is None, validation has failed, user is disabled or user not found

        user = await user_provider.retrieve_by_credentials(
            # Require parameters
            username=username,
            password=password,
            request=request,

            # Pass in options from auth config
            **provider.options,

            # Pass in options from the calling authenticator
            **kwargs,
        )

        # Do not throw error if no user or not validated here.  We let the middleware handle that
        return user

    # NO, needs to move
    def validate_permissions(self, user: User, scopes: List) -> None:
        """Validate logged in users permissions again route permissions"""

        # Superadmin is always allowed
        if user.superadmin: return

        # Get permissions defined on this route
        route_permissions = scopes.scopes

        # If route does not specify permissions, then anyone that is authenticated can access.
        if not route_permissions: return

        # Compare users permissions with route permissions
        for permission in route_permissions:
            if permission in user.permissions:
                # This is an OR, if any one of these, then pass
                return

        # No matching permissinos means they are logged in, but they don't have the proper permissions.
        raise PermissionDenied(route_permissions)

    # This can probably be private _ ??
    def auth_header(self, request) -> Tuple[str, str, str]:
        """Extract authorization header parts"""
        authorization = request.headers.get('Authorization')
        if not authorization: return (authorization, '', '')
        scheme, _, param = authorization.partition(' ')
        return authorization, scheme.lower(), param
