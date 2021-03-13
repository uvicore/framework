import uvicore
from base64 import b64decode
from uvicore.http import status
from uvicore.typing import Tuple, Dict
from uvicore.http import Request
from uvicore.support import module
from uvicore.support.dumper import dump, dd
from fastapi.security import SecurityScopes
from uvicore.http.exceptions import HTTPException, PermissionDenied, NotAuthenticated, InvalidCredentials
from uvicore.auth.middleware.auth import Auth

@uvicore.service()
class Basic(Auth):
    """Basic HTTP Authentication Route Middleware"""

    def __init__(self, config: Dict):
        self.config = config

    async def __call__(self, scopes: SecurityScopes, request: Request):
        dump('BASIC HERE')
        dump(scopes.__dict__, self.config)

        # Assume unauthorized
        authorized = False

        # Parse authorization header
        authorization, scheme, param = self.auth_header(request)

        # Define Basic Auth unauthorized header only if we are allowed to return them, else None
        unauthorized_headers = None
        if self.config.return_www_authenticate_header:
            unauthorized_headers = {'WWW-Authenticate': 'Basic'}
            if self.config.realm: unauthorized_headers = {'WWW-Authenticate': 'Basic realm="{}"'.format(self.config.realm)}

        # This authorization method not provided or attempted, goto next guard in middleware stack
        if not authorization or scheme != "basic":
            if self.config.return_www_authenticate_header:
                # Only add WWW-Authenticate header if configured.  If Basic auth is the LAST of the guard stack
                # and we are in Web guard, we can safely prompt the browser Login box
                raise NotAuthenticated(headers=unauthorized_headers)
            else:
                # Return None means goto next middleware in guard stack
                return None

        # Try to get the Basic Auth credentials
        try:
            data = b64decode(param).decode("ascii")
        except Exception:
            # No credentials defined from basic auth header
            raise InvalidCredentials(headers=unauthorized_headers)
        username, separator, password = data.partition(":")

        # Incomplete username or password provided
        if not separator: raise InvalidCredentials(headers=unauthorized_headers)

        # Get user and validate credentials
        user = await self.retrieve_user(username, password or '', self.config.provider)

        # If no user returned, validation has failed or user not found
        if user is None: raise InvalidCredentials(headers=unauthorized_headers)

        # Hack logout by uncommenting this once
        #raise InvalidCredentials(headers=unauthorized_headers)

        # Validate Permissions
        self.validate_permissions(user, scopes)

        # Authorization successful.
        # Add user to request in case we use it in a decorator, we can pull it out with request.scope.get('user')
        request.scope['user'] = user

        # Return user in case we are using this guard as a dependency injected route parameter
        return user
