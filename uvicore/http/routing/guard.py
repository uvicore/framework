import uvicore
from uvicore.http import Request
from uvicore.typing import Sequence
from fastapi.params import Security
from fastapi.security import SecurityScopes
from uvicore.support.dumper import dump, dd
from uvicore.contracts import User
from uvicore.http.exceptions import PermissionDenied


@uvicore.service()
class Guard(Security):
    """Uvicore HTTP Route Auth Guard"""

    def __init__(self, scopes: Sequence[str] = []):
        # Ensure scopes is a List, to allow for singles
        if scopes: scopes = [scopes] if isinstance(scopes, str) else list(scopes)

        # Call FastAPI Security Depends with our scope analyzer dependency
        super().__init__(dependency=Scopes(), scopes=scopes, use_cache=True)


class Scopes:

    async def __call__(self, security_scopes: SecurityScopes, request: Request) -> User:
        # Get scopes List.  These are permissions/scopes defined on this route
        scopes = list(security_scopes.scopes)

        # Get user from request.  Will always exist.  If not logged it will be
        # the anonymous user which may still have permissions/scopes to compare
        user: User = request.user
        dump('USER PERMISSIONS', user.permissions)

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

        dump('-----------------------------------------------------------------')
        dump('Auth Route Guard HERE:', scopes, user)
        dump('-----------------------------------------------------------------')

        if not authorized:
            # User does not have all route scopes, handle permission denied
            raise PermissionDenied(missing_scopes)
        else:
            return user

    def validate_permissions(self, user: User, scopes: SecurityScopes) -> None:
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
