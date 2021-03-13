import uvicore
from uvicore.http import status
from uvicore.http import Request
from uvicore.auth import User
from uvicore.support import module
from fastapi.params import Security
from fastapi.security import SecurityScopes
from uvicore.support.dumper import dump, dd
from uvicore.typing import Optional, Sequence, Callable, Any, List, Dict, Tuple
from uvicore.http.exceptions import HTTPException, PermissionDenied, NotAuthenticated, InvalidCredentials
from uvicore.contracts import UserProvider


@uvicore.service()
class Guard(Security):
    """Uvicore Auth Guard"""

    def __init__(self, scopes: Optional[Sequence[str]] = None, guard: str = None):
        # # Swap guard and scopes
        # if scopes is None and type(guard) == list:
        #     scopes: Sequence[str] = guard
        #     guard = None

        # Ensure scopes is a List, to allow for singles
        if scopes: scopes = [scopes] if isinstance(scopes, str) else list(scopes)

        # Do NOT apply a default guard to self.guard, let it be None
        # So I know its blank so I can overwrite it with a parent guard if needed
        self.scopes = scopes
        self.guard = guard

        # Get auth_config from app config
        auth_config = uvicore.config.app.auth

        # Set default guard if none providedGet actual guard from app config
        if guard is None: guard = auth_config.default

        # Get actual guard config
        if guard not in auth_config.guards:
            raise Exception('Guard {} not found in app config'.format(guard))
        guard_config = auth_config.guards[guard].clone()  # Clone becuase I add name below

        # Add name to guard config (its a clone, its ok)
        guard_config.name = guard

        # Get all providers from auth_config
        providers = auth_config.providers

        # Get all authenticator options from auth_config
        options = auth_config.options

        # Call parent Depends passing in the multi-middleware Authenticator
        super().__init__(dependency=Authenticator(guard_config, options, providers), scopes=scopes, use_cache=True)


@uvicore.service()
class Authenticator:
    def __init__(self, guard: Dict, options, providers: Dict):
        # Guard is the full config SuperDict from app config matching the proper guard string
        self.guard = guard

        # Authenticator Default Options
        self.options = options

        # Providers is all providers from app config
        self.providers = providers

    async def __call__(self, scopes: SecurityScopes, request: Request):
        #dump(self.guard)
        # Dict({
        #     'authenticators': Dict({
        #         'jwt': Dict({
        #             'module': 'uvicore.auth.middleware.Jwt',
        #             'verify_signature': True,
        #             'algorithms': ['RS256'],
        #             'secret':
        #                 '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnc84SDViVX8JNye2GVQZ\n'
        #                 'ixAwG2PWXoOhkj++wGASoAXs2LN0Ue48conxf/0bgEtq6kcbLPR23SieqBZA77vc\n'
        #                 'yulimMbzfwNczyP3FRo8wSCqRgJipTse87WItd8ga2MUCzSS8q19V4swUT4T23Su\n'
        #                 'DiG/Ry5f1sYbvxP2kJAJMUCzVbS7STxh33h65Bj+P6JdzrCJi+yrLqg928RHjLIF\n'
        #                 'gDy4MyFBLTI8w5u6IJi1TLm6h9lj3YqSa/qDkkIardnnZa7Xj0IJCEB9c+RD4Q7C\n'
        #                 '+jco6g2Vr9oLP8Mg3c5lZPNVzcXC67UMVk9lK+zrlfPDI/m2+9kyTc/58S9ZUTFJ\nQwIDAQAB\n-----END PUBLIC KEY-----'
        #         }),
        #         'basic': Dict({
        #             'module': 'uvicore.auth.middleware.Basic',
        #             'provider': 'users',
        #             'realm': 'App1'
        #         })
        #     }),
        #     'name': 'api'
        # })

        for authenticator in self.guard.authenticators.values():
            # Get authenticator options by deep merging defaults and proper providers
            options = authenticator.clone()
            if 'options' in options:
                # Deep merge default options
                option_key = options.options
                if option_key not in self.options:
                    # This is an application error, not an HTTPException
                    raise Exception('Default options key {} not found in app config'.format(option_key))
                options.defaults(self.options[option_key])  # Merge seems to do a clone too!

            # Merge provider into options
            if 'provider' in options:
                if options.provider not in self.providers:
                    # This is an application error, not an HTTPException
                    raise Exception('Provider {} not found in app config'.format(options.provider))
                options.provider = self.providers[options.provider].clone()

            options.guard = self.guard.name

            #dump(options)
            # Dict({
            #     'default_options': 'jwt',
            #     'module': 'uvicore.auth.middleware.Jwt',
            #     'provider': Dict({
            #         'module': 'uvicore.auth.models.user.User',
            #         'method': 'userinfo',
            #         'model': 'uvicore.auth.models.user.User',
            #         'includes': ['roles', 'roles.permissions', 'groups', 'groups.roles', 'groups.roles.permissions']
            #     }),
            #     'sync': Dict({'auto_create_user': True}),
            #     'verify_signature': True,
            #     'audience': '222b06eb-85ce-472b-af30-ec09244e3bf0',
            #     'algorithms': ['RS256'],
            #     'secret':
            #         '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnc84SDViVX8JNye2GVQZ\n'
            #         'ixAwG2PWXoOhkj++wGASoAXs2LN0Ue48conxf/0bgEtq6kcbLPR23SieqBZA77vc\n'
            #         'yulimMbzfwNczyP3FRo8wSCqRgJipTse87WItd8ga2MUCzSS8q19V4swUT4T23Su\n'
            #         'DiG/Ry5f1sYbvxP2kJAJMUCzVbS7STxh33h65Bj+P6JdzrCJi+yrLqg928RHjLIF\n'
            #         'gDy4MyFBLTI8w5u6IJi1TLm6h9lj3YqSa/qDkkIardnnZa7Xj0IJCEB9c+RD4Q7C\n'
            #         '+jco6g2Vr9oLP8Mg3c5lZPNVzcXC67UMVk9lK+zrlfPDI/m2+9kyTc/58S9ZUTFJ\nQwIDAQAB\n-----END PUBLIC KEY-----'
            # })

            # Import the auth middleware module
            middleware = module.load(options.module).object(options)

            # Fire the middleware __call__ callable and get the returned value
            value = await middleware(scopes, request)

            # If value is returned, auth was successful with this authenticator.  Return value, stop the middleware stack.
            # If value is None means auth headers not found.  Continue to next middleware in auth stack
            if value is not None:
                return value

        # If we are here, no auth middleware returned a value, meaning NOT logged in
        # If no value is ever returned we are not logged in.
        # Maybe here is the place to add an anonymous user to the request? with user.authenticated = False ???????
        # NO, think about this.  If a route is NOT guarded, this code will never run therefore request.user will
        # never exist.  Would have to do global auth middleware to accomplish an always present anonymous user.
        # I could have a built-in hidden global middleware that adds request.user as an anonymous model?
        raise NotAuthenticated('MASTER STACKER')


@uvicore.service()
class Auth:
    """Base Auth middleware class"""

    async def retrieve_user(self, username: str, password: str, provider: Dict) -> Optional[User]:
        """Retrieve user from User Provider backend"""
        # Import our user provider defined in auth config
        user_provider: UserProvider = module.load(provider.module).object()

        # Get user from user provider and validate password
        # If returned user is None, validation has failed, user is disabled or user not found
        user = await user_provider.retrieve_by_credentials(username, password, **provider.options)

        # Do not throw error if no user or not validated here.  We let the middleware handle that
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

    def auth_header(self, request) -> Tuple[str, str, str]:
        """Extract authorization header parts"""
        authorization = request.headers.get('Authorization')
        if not authorization: return (authorization, '', '')
        scheme, _, param = authorization.partition(' ')
        return authorization, scheme.lower(), param
