import uvicore
from base64 import b64decode
from uvicore.contracts import User
from uvicore.support.dumper import dump, dd
from uvicore.http.request import HTTPConnection
from uvicore.typing import Dict, Optional, Union
from uvicore.auth.authenticators.base import Authenticator


@uvicore.service()
class Basic(Authenticator):
    """HTTP basic auth authenticator"""

    # Notice:  Do not ever throw or return an error from authenticators.
    # If there is any auth problem (no headers, invalid or expired tokens, bad password)
    # then return True or False instead.  Any issues or invalid credentials causes the global
    # Authentication middleware to inject an Anonymous user, not to throw errors.
    # Any permissions errors happen at a route level when checking of the route
    # require an authenticated user or valid scope/role.

    # Return of False means this authorization method is not being attempted
    # Return of True means this authorization method was being attempted, but failed validation
    # Return of User object means a valid user was found

    async def authenticate(self, request: HTTPConnection) -> Union[User, bool]:
        dump('BASIC Authenticator HERE')

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
            # Return of False means this authorization method is not being attempted
            return False

        # Try to get the Basic Auth credentials
        try:
            data = b64decode(param).decode("ascii")
        except Exception:
            # No credentials defined from basic auth header
            return True

        # Get username and password from basic auth header
        username, separator, password = data.partition(":")

        # Incomplete username or password provided
        #if not separator: return InvalidCredentials(headers=unauthorized_headers)
        if not separator: return True

        # Get user and validate credentials
        user: User = await self.retrieve_user(username, password or '', self.config.provider, request)

        # If no user returned, validation has failed or user not found
        #if user is None: return InvalidCredentials(headers=unauthorized_headers)
        #if user is None: return InvalidCredentials(headers=unauthorized_headers)

        # Hack logout by uncommenting this once
        #return InvalidCredentials(headers=unauthorized_headers)

        # Return user.  Could be none if not authenticated or user object of authenticated
        return user
