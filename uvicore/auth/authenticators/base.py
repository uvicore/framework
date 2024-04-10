import uvicore
from uvicore.support import module
from uvicore.support.dumper import dump, dd
from uvicore.http.request import HTTPConnection
from uvicore.contracts import UserInfo, UserProvider
from uvicore.typing import Dict, Optional, List, Tuple
from uvicore.contracts import Logger as LoggerInterface
from uvicore.contracts import Authenticator as AuthenticatorInterface


@uvicore.service()
class Authenticator(AuthenticatorInterface):
    """Base authenticator class"""

    def __init__(self, config: Dict):
        self.config = config

    @property
    def log(self) -> LoggerInterface:
        return uvicore.log.name('uvicore.auth')

    async def retrieve_user(self, username: str, password: str, provider: Dict, request: HTTPConnection, **kwargs) -> Optional[UserInfo]:
        """Retrieve user from User Provider backend"""

        # Import user provider defined in auth config
        user_provider: UserProvider = module.load(provider.module).object()

        # Get user from user provider and validate password.  User will be Anonymous
        # if user not found, disabled or validation failed
        user = await user_provider.retrieve_by_credentials(
            # Require parameters
            username=username,
            password=password,
            request=request,

            # Pass in options from auth config
            **provider.options,

            # Pass in options from the calling authenticator
            **kwargs,
        )

        # Do not throw error if no user or not validated here.  We let the middleware handle that
        return user

    async def create_user(self, provider: Dict, request: HTTPConnection, **kwargs):
        # Import user provider defined in auth config
        user_provider: UserProvider = module.load(provider.module).object()

        # Create user from user provider
        # Returned user is actual backend user, NOT Auth User object
        user = await user_provider.create_user(request, **kwargs)
        return user

    async def sync_user(self, provider: Dict, request: HTTPConnection, **kwargs):
        # Import user provider defined in auth config
        user_provider: UserProvider = module.load(provider.module).object()

        # Create user from user provider
        # Returned user is actual backend user, NOT Auth User object
        user = await user_provider.sync_user(request, **kwargs)
        return user

    def auth_header(self, request) -> Tuple[str, str, str]:
        """Extract authorization header parts"""
        authorization = request.headers.get('Authorization')
        if not authorization: return (authorization, '', '')
        # Partition is a bit more performant that split
        scheme, _, param = authorization.partition(' ')
        return authorization, scheme.lower(), param
