import uvicore
from base64 import b64decode
from uvicore.contracts import UserInfo
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

    # Return of False means this authentication method is not being attempted, try next authenticator
    # Return of True means this authentication method was being attempted, but failed validation, skip next authenticator
    # Return of User object means a valid user was found, skip next authenticator

    async def authenticate(self, request: HTTPConnection) -> Union[UserInfo, bool]:
        # 8500 req/sec
        #self.log.debug('BASIC Authenticator')
        # 7315 req/sec, logging is slow

        # Parse authorization header
        authorization, scheme, param = self.auth_header(request)

        # This authentication method not provided or attempted, goto next authenticator
        if not authorization or scheme != "basic":
            # Return of False means this authentication method is not being attempted
            # goto next authenticator in stack
            #self.log.debug('No Basic Auth header, goto next authenticator in stack')
            return False

        # Try to get the Basic Auth credentials
        try:
            data = b64decode(param).decode("ascii")
        except Exception:
            # No credentials defined from basic auth header, return True to denote Anonymous user and skip next authenticator
            self.log.debug('No credentials found in Basic Auth Header, seen as anonymous')
            return True

        # Get username and password from basic auth header
        username, separator, password = data.partition(":")

        # Incomplete username or password provided
        if not separator: return True

        # Get user and validate credentials
        user: UserInfo = await self.retrieve_user(username, password or '', self.config.provider, request)

        # Return user.  If no user return True to denote Anonymous User and skip next authenticator
        return user or True
