import uvicore
from uvicore.http import Request
from uvicore.typing import Sequence
from fastapi.params import Security
from fastapi.security import SecurityScopes
from uvicore.support.dumper import dump, dd
from uvicore.contracts import UserInfo
from uvicore.http.exceptions import PermissionDenied, NotAuthenticated, HTTPException
from uvicore.http.response import Redirect


@uvicore.service()
class Guard(Security):
    """Uvicore HTTP Route Auth Guard"""

    def __init__(self, scopes: Sequence[str] = []):
        # Ensure scopes is a List, to allow for singles
        if scopes: scopes = [scopes] if isinstance(scopes, str) else list(scopes)

        # Call FastAPI Security Depends with our scope analyzer dependency
        super().__init__(dependency=Scopes(), scopes=scopes, use_cache=True)


class Scopes:

    @property
    def log(self):
        return uvicore.log.name('uvicore.http')

    async def __call__(self, security_scopes: SecurityScopes, request: Request) -> UserInfo:
        # Get scopes List.  These are permissions/scopes defined on this route
        scopes = list(security_scopes.scopes)
        self.log.debug('Auth guard scopes required for {}: {}'.format(request.scope['path'], str(scopes)))

        # Get user from request.  Will always exist.  If not logged it will be
        # the anonymous user which may still have permissions/scopes to compare
        user: UserInfo = request.user
        self.log.debug('Auth guard user: {}'.format(str(user)))

        # If no scopes, allow access
        if not scopes: return user

        # Superadmin always wins, never check scopes
        if user.superadmin: return user

        # User must have ALL scopes defined on the route (an AND statement)
        authorized = True
        missing_scopes = []
        for scope in scopes:
            if scope not in user.permissions:
                authorized = False
                missing_scopes.append(scope)

        # dump('-----------------------------------------------------------------')
        # dump('Auth Route Guard HERE:', scopes, user)
        # dump('-----------------------------------------------------------------')

        # Hack logout of basic auth
        #raise NotAuthenticated(headers={'WWW-Authenticate': 'Basic realm="App1 Web Realm"'})

        # Authorized and authenticated.  Return user in case Guard() is being used
        # as a route parameter using FastAPI Depends.  User will be injected back to param value.
        if authorized: return user

        # Not authorized or possibly even authenticated
        # Get unauthenticated handler from auth config
        # Route type (web or api) is added to request.scope from authentication middleware
        route_type = request.scope.get('route_type') or 'api'

        # Get the route auth config based on route_type
        auth_config = uvicore.config.app.auth[route_type]

        # Default unauthenticated is to raise exception.
        # Check for redirect override or additional exception headers
        if auth_config.unauthenticated_handler.redirect:
            location = auth_config.unauthenticated_handler.redirect
            if '/' not in location and '.' in location: location = request.url_for(location)
            separator = '&' if '?' in location else '?'
            referer = separator + "referer=" + str(request.scope.get('path'))
            raise HTTPException(status_code=301, headers={
                'Location': location + referer
            })

        # Check for additional exception headers
        exception_headers = None
        if auth_config.unauthenticated_handler.exception:
            exception_headers = auth_config.unauthenticated_handler.exception.headers

        if user.authenticated:
            # User authenticated but does not have all route scopes
            raise PermissionDenied(missing_scopes, headers=exception_headers)
        else:
            # User is not even logged in
            raise NotAuthenticated(headers=exception_headers)

    def validate_permissions(self, user: UserInfo, scopes: SecurityScopes) -> None:
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
