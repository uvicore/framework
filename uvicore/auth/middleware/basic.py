import uvicore
from base64 import b64decode
from uvicore.http import status
from uvicore.typing import Tuple, Dict
from uvicore.http import Request
from uvicore.auth import UserInfo
from uvicore.support import module
from uvicore.support.dumper import dump, dd
from fastapi.security import SecurityScopes
from uvicore.http.exceptions import HTTPException


@uvicore.service()
class Basic:
    """Basic Auth Route Middleware"""

    def __init__(self, guard: str, provider: Dict):
        self.guard = guard
        self.provider = provider

    async def __call__(self, scopes: SecurityScopes, request: Request):
        dump(scopes.__dict__, self.guard)

        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        # Define Basic Auth unauthorized header
        unauthorized_headers = {"WWW-Authenticate": "Basic"}

        # If not yet authorized, send Basic Auth headers
        if not authorization or scheme.lower() != "basic":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers=unauthorized_headers,
            )

        # Define invalid authentication credentials exception
        invalid_user_credentials_exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
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
        user_model = module.load(self.provider.module).object
        user_method = getattr(user_model, self.provider.method)
        user: UserInfo = await user_method(**{
            'provider': self.provider,
            'username': username,
            'password': password or '',  # Must not be None or no validation takes places
        })

        # If user returned, password has been validated
        if user: authorized = True

        # Hack logout by uncommenting this once
        #raise invalid_user_credentials_exc

        # Get Route Permissions
        route_permissions = scopes.scopes

        # Compare users permissions with endpoint permissions (unless superadmin, always pass)
        # If no route premissions, then anyone logged in can access the route, no restrictions except authenticated
        if authorized and route_permissions and user.superadmin == False:
            authorized = False
            for permission in route_permissions:
                if permission in user.permissions:
                    # This is an OR, if any one of these, then pass
                    authorized = True
                    break
            if not authorized:
                # This means they are logged in, but they don't have the proper permissions.
                # So show access denied, not a prompt for password
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid permissions",
                )


        if authorized:
            # Add user to request in case we use it in a decorator, we can pull it out with request.scope.get('user')
            request.scope['user'] = user

            # Return user in case we are using this guard as a dependency injected FastAPI parameter
            return user
        else:
            # Not authorized, return invalid credentials 401
            raise invalid_user_credentials_exc


def get_authorization_scheme_param(authorization_header_value: str) -> Tuple[str, str]:
    if not authorization_header_value:
        return "", ""
    scheme, _, param = authorization_header_value.partition(" ")
    return scheme, param
