import jwt
import uvicore
from uvicore.support.dumper import dump, dd
from uvicore.http.request import HTTPConnection
from uvicore.typing import Dict, Optional, Union
from uvicore.auth.authenticators.base import Authenticator
from uvicore.http.exceptions import NotAuthenticated, InvalidCredentials, HTTPException
from uvicore.contracts import User

@uvicore.service()
class Jwt(Authenticator):
    """JWT bearer token authenticator"""

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
        dump('JWT Authenticator HERE')

        # Parse authorization header
        authorization, scheme, token = self.auth_header(request)

        # This authorization method not provided or attempted, goto next authenticator
        if not authorization or scheme != "bearer":
            # Return of False means this authorization method is not being attempted
            return False

        # Decode JWT
        try:
            if self.config.verify_signature:
                # With secret algorithm validation
                dump('WITH Validation')
                payload = Dict(jwt.decode(token, self.config.secret, audience=self.config.audience, algorithms=self.config.algorithms))
            else:
                # Without validation
                dump('WITHOUT Validation')
                payload = Dict(jwt.decode(token, options={"verify_signature": False}))

                # Validate aud claim
                # jwt.decode also validates the aud claim.  Since we are skipping validation, we'll still validate aud claim here.
                if payload.aud != self.config.audience:
                    # No exception, just return None to denote Anonymous
                    return True
                    # return HTTPException(
                    #     status_code=status.HTTP_401_UNAUTHORIZED,
                    #     detail="Invalid audience",
                    # )

        except Exception as e:
            # Issue with validation.  Bad key, token expired...
            # Pass JWT library exception message right through with a generic 401
            # return HTTPException(
            #     status_code=401,
            #     detail=str(e),
            # )
            # No exception, just return None to denote Anonymous
            return True

        #dump('JWT', payload)

        # Get user and validate credentials
        #user: User = await self.retrieve_user(payload.email, None, self.config.provider, request, jwt=payload)
        user: User = await self.retrieve_user(payload.email, None, self.config.provider, request, jwt=payload)

        # If user is none and auto_create_user is enabled, auto-create user
        # Link user up to groups table based on JWT roles
        # Now self.get_user again

        # If no user returned, validation has failed or user not found
        #if user is None: raise InvalidCredentials()

        # Validate Permissions
        #self.validate_permissions(user, scopes.scopes)

        # Authorization successful.
        # Add user to request in case we use it in a decorator, we can pull it out with request.scope.get('user')
        #request.scope['user'] = user

        # Return user.  Could be none if not authenticated or user object of authenticated
        return user
