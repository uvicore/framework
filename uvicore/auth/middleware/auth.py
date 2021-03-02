import uvicore
from fastapi.params import Depends
from fastapi.security import SecurityScopes
from uvicore.http.exceptions import HTTPException
from uvicore.http.status import HTTP_401_UNAUTHORIZED, HTTP_429_TOO_MANY_REQUESTS
from uvicore.typing import Optional, Sequence, Dict, Tuple, Decorator
from uvicore.http import Request
from uvicore.support.dumper import dump, dd
from base64 import b64decode
from uvicore.support import module
from uvicore.auth.models import User
from uvicore.http.middleware import Security
from uvicore.http.middleware.security import SecurityBase

def get_authorization_scheme_param(authorization_header_value: str) -> Tuple[str, str]:
    if not authorization_header_value:
        return "", ""
    scheme, _, param = authorization_header_value.partition(" ")
    return scheme, param


@uvicore.service()
class Guard(Security):
    """Auth middleware"""
    pass

@uvicore.service()
class Basic:

    def __init__(self, guard: str):
        self.guard = guard

    async def __call__(self, scopes: SecurityScopes, request: Request):
        dump(scopes.__dict__, self.guard)

        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        # Define Basic Auth unauthorized header
        unauthorized_headers = {"WWW-Authenticate": "Basic"}

        # If not yet authorized, send Basic Auth headers
        if not authorization or scheme.lower() != "basic":
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers=unauthorized_headers,
            )

        # Define invalid authentication credentials exception
        invalid_user_credentials_exc = HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers=unauthorized_headers,
        )

        # Get the Basic Auth user/pass
        try:
            data = b64decode(param).decode("ascii")
        except Exception:
            raise invalid_user_credentials_exc
        username, separator, password = data.partition(":")
        if not separator: raise invalid_user_credentials_exc

        authorized = False

        # Get user query method
        config = uvicore.config.app.auth
        user_model = module.load(config.user_model).object
        user_method = getattr(user_model, config.user_method)
        user = await user_method(**{
            config.user_username_field: username,
            config.user_password_field: password
        })
        #return
        if user: authorized = True
        #raise invalid_user_credentials_exc  # Hack logout

        # Validate permissions
        # Does this user have any one of these permissions (and or or?)
        permissions = scopes.scopes

        # Get users permissions
        #user_permissions = ['posts.read', 'auth_users.read']
        #user_permissions = ['posts.read']

        if authorized and permissions:
            authorized = False
            for permission in permissions:
                if permission in user.permissions:
                    # This is an OR, if any one of these, then pass
                    authorized = True
                    break
            if not authorized:
                # This means they are logged in, but they don't have the proper permissions.
                # So show access denied, not a prompt for password
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Invalid permissions",
                )


        if authorized:
            # Fixme, user permissins should be on model, for now just add to
            # request.  When fixed, also fix ModelRouter when it grabs permissions in guard_include_permissions
            request.scope['user_permissions'] = user.permissions

            # Also add user to request in case we use it in a decorator, we can pull it out
            request.scope['user'] = user

            return user
        else:
            raise invalid_user_credentials_exc


        # # First, check if logged in at all, if NOT, 404
        # # ...

        # # If logged in...
        # # Allowed permissions
        # permissions = scopes.scopes

        # # Get user somehow, either from JWT, Session, Basic Auth Header...
        # user = 'mreschke@sunfinity.com'

        # # Ensure this user has the above permissions
        # authorized = False

        # if authorized:
        #     # Authorized, return logged in User model
        #     return await User.query().include('contact', 'info').find(1)
        # else:
        #     # Not authorized
        #     raise HTTPException(
        #         status_code=HTTP_401_UNAUTHORIZED,
        #         detail="Not authenticated",
        #         headers={"WWW-Authenticate": "Bearer"},  # Change depending on session, basic etc...
        #     )
