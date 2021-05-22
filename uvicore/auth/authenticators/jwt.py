import uvicore
from jwt import decode
from uvicore.support.dumper import dump, dd
from uvicore.http.request import HTTPConnection
from uvicore.typing import Dict, Optional, Union, Callable
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

    # Return of False means this authentication method is not being attempted, try next authenticator
    # Return of True means this authentication method was being attempted, but failed validation, skip next authenticator
    # Return of User object means a valid user was found, skip next authenticator

    async def authenticate(self, request: HTTPConnection) -> Union[User, bool]:
        #dump('JWT Authenticator HERE')

        # Parse authorization header
        authorization, scheme, token = self.auth_header(request)

        # This authentication method not provided or attempted, goto next authenticator
        if not authorization or scheme != "bearer":
            # Return of False means this authentication method is not being attempted
            # goto next authenticator in stack
            return False

        # Detect anonymous API access.
        # API gateways that allow anonymous access to an API will pass the request
        # downstream even if the token is missing, invalid or expired.
        # When they do, they add a header notifying downstream that auth has failed
        # but anonymous access is still allowed.  For Kong this header is x-anonymous-consumer
        # If the API gateway does not allow anonymous access, downstream won't even be proxied.
        #dump(request.headers)
        if (self.config.anonymous_header and self.config.anonymous_header in request.headers):
            # Anonymous header found, return True to denote Anonymous user and skip next authenticator
            return True

        # Decode JWT with or without verification
        jwt = None
        try:
            if self.config.verify_signature:
                # With secret algorithm validation
                #dump('WITH Validation')
                jwt = Dict(decode(token, self.config.secret, audience=self.config.audience, algorithms=self.config.algorithms))
            else:
                # Without validation
                #dump('WITHOUT Validation')
                jwt = Dict(decode(token, options={"verify_signature": False}))

                # Validate aud claim
                # jwt.decode also validates the aud claim.  Since we are skipping validation, we'll still validate aud claim here.
                if jwt.aud != self.config.audience:
                    # Audience mismatch, return True to denote Anonymous user and skip next authenticator
                    return True
        except Exception as e:
            # Issue with validating JWT, return True to denote Anonymous user and skip next authenticator
            return True

        #dump('JWT', jwt)

        # Get user and validate credentials
        user: User = await self.retrieve_user(jwt.email, None, self.config.provider, request, jwt=jwt)

        # User from valid JWT not found in uvicore OR not synced for first time (no uuid).
        # Auto create or update user if allowed in config
        if self.config.auto_create_user and (user is None or user.uuid is None):
            jwt_mapping = self.config.auto_create_user_jwt_mapping
            new_user = {}
            for key, value in self.config.auto_create_user_jwt_mapping.items():
                if isinstance(value, Callable):
                    new_user[key] = value(jwt)
                else:
                    new_user[key] = value

            # User does not exist, create user
            if user is None:
                # Auto create new user in user provider
                await self.create_user(self.config.provider, request, **new_user)

            else:
                # User exists, but needs an initial sync
                await self.sync_user(self.config.provider, request, **new_user)

            # Get user and validate credentials
            user: User = await self.retrieve_user(jwt.email, None, self.config.provider, request, jwt=jwt)


            # Dict({
            #     'aud': 'd709a432-5edc-44c7-8721-4cf123473c45',
            #     'exp': 1616000280,
            #     'iat': 1615996680,
            #     'iss': 'https://auth-local.sunfinity.com',
            #     'sub': '217e27b4-0e0a-464c-84a8-c40312b55801',
            #     'authenticationType': 'PASSWORD',
            #     'email': 'it@sunfinity.com',
            #     'email_verified': True,
            #     'applicationId': 'd709a432-5edc-44c7-8721-4cf123473c45',
            #     'roles': ['Administrator'],
            #     'name': 'Admin|Istrator'
            # })


        # If user is none and auto_create_user is enabled, auto-create user
        # Link user up to groups table based on JWT roles
        # Now self.get_user again

        # If no user returned, validation has failed or user not found
        #if user is None: raise InvalidCredentials()

        # Validate Permissions
        #self.validate_permissions(user, scopes.scopes)

        # Authentication successful.
        # Add user to request in case we use it in a decorator, we can pull it out with request.scope.get('user')
        #request.scope['user'] = user

        # Return user.  If no user return True to denote Anonymous User and skip next authenticator
        return user or True
