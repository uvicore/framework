import uvicore
from base64 import b64decode
from uvicore.contracts import User
from uvicore.support.dumper import dump, dd
from uvicore.http.request import HTTPConnection
from uvicore.typing import Dict, Optional
from uvicore.auth.authenticators.base import Authenticator


@uvicore.service()
class Basic(Authenticator):
    """HTTP basic auth authenticator"""

    # Notice:  Do not ever throw or return an error from authenticators.
    # If there is any auth problem (no headers, invalid or expired tokens, bad password)
    # then return None instead.  Any issues or invalid credentials causes the global
    # Authentication middleware to inject an Anonymous user, not to throw errors.
    # Any permissions errors happen at a route level when checking of the route
    # require an authenticated user or valid scope/role.

    def __init__(self, config: Dict):
        self.config = config

    async def authenticate(self, request: HTTPConnection) -> Optional[User]:
        # Parse authorization header
        authorization, scheme, param = self.auth_header(request)

        # Define Basic Auth unauthoridzed header only if we are allowed to return them, else None
        # NO, not here, we don't care if you are logged in
        # unauthorized_headers = None
        # if self.config.return_www_authenticate_header:
        #     unauthorized_headers = {'WWW-Authenticate': 'Basic'}
        #     if self.config.realm: unauthorized_headers = {'WWW-Authenticate': 'Basic realm="{}"'.format(self.config.realm)}

        # This authorization method not provided or attempted, goto next authenticator
        if not authorization or scheme != "basic":
            # Return None means goto next authenticator in authorization middleware
            return None
            # NO
            # if self.config.return_www_authenticate_header:
            #     # Only add WWW-Authenticate header if configured.  If Basic auth is the LAST of the guard stack
            #     # and we are in Web guard, we can safely prompt the browser Login box
            #     return NotAuthenticated(headers=unauthorized_headers)
            # else:
            #     # Return None means goto next authenticator in authorization middleware
            #     return None

        # Try to get the Basic Auth credentials
        try:
            data = b64decode(param).decode("ascii")
        except Exception:
            # No credentials defined from basic auth header
            return None
            #return InvalidCredentials(headers=unauthorized_headers)

        # Get username and password from basic auth header
        username, separator, password = data.partition(":")

        # Incomplete username or password provided
        #if not separator: return InvalidCredentials(headers=unauthorized_headers)
        if not separator: return None

        # Get user and validate credentials
        user: User = await self.retrieve_user(username, password or '', self.config.provider, request)

        # If no user returned, validation has failed or user not found
        #if user is None: return InvalidCredentials(headers=unauthorized_headers)
        #if user is None: return InvalidCredentials(headers=unauthorized_headers)

        # Hack logout by uncommenting this once
        #return InvalidCredentials(headers=unauthorized_headers)

        # Return user.  Could be none if not authenticated or user object of authenticated
        return user
