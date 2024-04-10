import uvicore
from uvicore.typing import Dict, Callable, ASGIApp, Send, Receive, Scope
from uvicore.http.response import Text, HTML, JSON, Response
from uvicore.http.request import HTTPConnection, Request
from uvicore.support.dumper import dump, dd
from uvicore.support import module
from uvicore.http.exceptions import HTTPException
from uvicore.contracts import Authenticator, UserInfo, UserProvider


@uvicore.service()
class Authentication:
    """Authentication global middleware capable of multiple authenticator backends"""

    def __init__(self, app: ASGIApp, route_type: str) -> None:
        # __init__ called one time on uvicore HTTP bootstrap
        # __call__ called on every request
        self.app = app
        self.route_type = str(route_type or 'api').lower()
        assert self.route_type in ['web', 'api']

        # Load and merge the auth config for this route type (web or api)
        self.config = get_auth_config(self.route_type)

        # Variable caching
        # Middleware needs to be fast.  Really fast!
        # Even saving a few CPU cycles here and there makes a huge different
        # with a high concurrency site (or wrk benchmark).  So I use variable
        # caching to load, instantiate, clone...ONCE.  So __call__ need to be efficient.
        self.cached_authenticators = {}
        self.cached_providers = {}
        self.cached_default_provider_options = {}
        self.cached_default_provider_method = None

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # Middleware only for http and websocket types
        if scope["type"] not in ["http", "websocket"]:
            # Next middleware in stack
            await self.app(scope, receive, send)
            return

        # Get the http connection.  This is essentially the Request but not HTTP specific.
        # The base connection that works for HTTP and WebSockets.  Request inherits from HTTPConnection
        request = HTTPConnection(scope)

        # Loop each authenticator until one is a success
        user = None
        authenticator_name = None
        for authenticator_name, authenticator in self.config.authenticators.items():
            # Load authenticator backend from cache or module.load()
            if authenticator_name in self.cached_authenticators:
                #dump('cached authenticator')
                backend = self.cached_authenticators[authenticator_name]
            else:
                try:
                    # Load authenticator and instantiate it, saving the instance to our cached_authenticators
                    # This essentially makes the instance a singleton, which is fine because it is
                    # the 'authenticate' method that is called per request.  One instance is fine.
                    backend: Authenticator = module.load(authenticator.module).object(authenticator)
                    self.cached_authenticators[authenticator_name] = backend
                except Exception as e:
                    raise Exception('Issue trying to import authenticator module defined in app.auth config - {}'.format(str(e)))

            # Call backend authenticate() method
            # Return of False means this authentication method is not being attempted, try next authenticator
            # Return of True means this authentication method was being attempted, but failed validation, skip next authenticator
            # Return of User object means a valid user was found, skip next authenticator
            #dump(backend)
            # 8867 req/sec
            user = await backend.authenticate(request)
            # 6924 req/sec logging, 8500 req/sec without logging

            # Determine if we should continue to next authenticator
            # Return of True means this authorization method was being attempted, but failed validation
            # This means we can SKIP the next authenticators as they are not being attempted.
            if isinstance(user, bool) and user == True:
                break

            # If User object returned, validation success, stop authenticator itteration
            if isinstance(user, UserInfo):
                break

            # Check for exception and return
            # Should never happen as authenticators never produce an Exception
            # But if it ever does, then I can handle it properly here
            if isinstance(user, HTTPException):
                return await self.error_response(user, scope, receive, send)

        # If valid user is logged in, append 'authenticated' to permissions
        if isinstance(user, UserInfo):
            if 'authenticated' not in user.permissions:
                user.permissions.insert(0, 'authenticated')

        # Retrieve anonymous user from default_provider backend
        # If all authenticators returned no User object, user is not logged in with any method.
        # Build an anonymous user object to inject into the request scope
        if not isinstance(user, UserInfo):
            # 8350 req/sec
            user = await self.retrieve_anonymous_user(request)
            # 6600 req/sec - even though I am now using ARRAY cache store
            # to store the user.  This must mean pickle is slowing it down.
            # 7500 without pickel!  Don't think array needs pickling because
            # its already python!

            # Ensure authenticated is False
            user.authenticated = False

            # No, will never happen, its a new user
            # if 'authenticated' in user.permissions:
            #     user.permissions.remove('authenticated')

        # Add user to request
        scope['user'] = user
        #scope["auth"] = user.permissions  # No, this was starlette example of where to place scopes

        # Add route_type (web or api) to request for guard.py usage
        scope['route_type'] = self.route_type

        # Add matched authenticator to request for later usage (like logout functionality)
        scope['authenticator'] = authenticator_name

        # Next global middleware in stack
        await self.app(scope, receive, send)

    async def retrieve_anonymous_user(self, request: HTTPConnection):
        """Retrieve anonymous user from User Provider backend"""
        # Import user provider defined in auth config
        provider_module = self.config.default_provider.module

        if provider_module in self.cached_providers:
            #dump('cached provider')
            user_provider = self.cached_providers[provider_module]
        else:
            #dump('UNcached provider')
            # Anonymous user provider is always the 'default_provider'
            # Load and instantiate just once, then cache the results, a huge boost for middleware!
            user_provider: UserProvider = module.load(self.config.default_provider.module).object()
            self.cached_providers[provider_module] = user_provider

        # Get additional provider kwargs from options and anonymous_options config
        if not self.cached_default_provider_options:
            # Cached because of the .clone(), this is a nice boost for middleware!
            self.cached_default_provider_options = self.config.default_provider.options.clone()
            self.cached_default_provider_options.merge(self.config.default_provider.anonymous_options)  # Anonymous wins in merge

        # Alter provider method called based on existence of username, id, or uuid parameters
        if not self.cached_default_provider_method:
            # No need to perform an 'in' statement on each request.  The first request
            # simply cache the default providers retrieval method
            self.cached_default_provider_method = user_provider.retrieve_by_username
            if 'id' in self.cached_default_provider_options: self.cached_default_provider_method = user_provider.retrieve_by_id
            if 'uuid' in self.cached_default_provider_options: self.cached_default_provider_method = user_provider.retrieve_by_uuid

        # Call user provider method passing in defined self.cached_default_provider_options
        # 57600 req/sec
        return await self.cached_default_provider_method(request=request, **self.cached_default_provider_options)
        # 51489. req/sec
        # Wow, this call to retrieve user is a bit slow, even with 'array' cache forced without pickle.

    async def error_response(self, user: UserInfo, scope: Scope, receive: Receive, send: Send):
        """Build and return error response"""
        if self.route_type == 'web':
            # Fixme, how can I use the user customized 401 HTML?
            response = HTML(
                content='401 HTML here? - {}'.format(user.detail),
                status_code=user.status_code,
                headers=user.headers
            )
        else:
            response = JSON(
                content={'message': user.detail},
                status_code=user.status_code,
                headers=user.headers
            )
        if scope["type"] == "websocket":
            await send({"type": "websocket.close", "code": 1000})
        else:
            await response(scope, receive, send)
        return



# Stand-alone function because we use this elsewhere outside the Authentication class
def get_auth_config(route_type: str = 'aip'):
    """Get web or api auth config and merge default options and providers"""

    # Load all default option configs
    default_options = uvicore.config.app.auth.default_options

    # Load all provider configs
    providers = uvicore.config.app.auth.providers

    # Merge default options and providers into each authenticator
    config_path = 'app.auth.api'
    if route_type == 'web': config_path = 'app.auth.web'
    config = uvicore.config.dotget(config_path).clone()

    # Merge provider Dict if specified as a string
    if 'default_provider' in config and isinstance(config.default_provider, str):
        if config.default_provider in providers:
            config.default_provider = providers[config.default_provider].clone()
        else:
            raise Exception("Default options '{}' not found in auth config".format(config.default_provider))

    # Merge each providers configuration
    for authenticator in config.authenticators.values():

        # Merge default_options Dict if specified as a string
        if 'default_options' in authenticator:
            # Deep merge default options
            if authenticator.default_options in default_options:
                authenticator.defaults(default_options[authenticator.default_options])  # Defaults does a clone!
            else:
                raise Exception("Default options '{}' not found in auth config".format(authenticator.default_options))

        # If no provider specified, use default_provider (already a full Dict from above)
        if 'provider' not in authenticator:
            authenticator.provider = config.default_provider

        # Merge provider Dict if specified as a string
        if 'provider' in authenticator and isinstance(authenticator.provider, str):
            if authenticator.provider in providers:
                authenticator.provider = providers[authenticator.provider].clone()
            else:
                raise Exception("Provider '{}' not found in auth config".format(authenticator.provider))

    # Returned merge config for all authenticators
    return config




















# import typing

# from starlette.authentication import (
#     AuthCredentials,
#     AuthenticationBackend,
#     AuthenticationError,
#     UnauthenticatedUser,
# )
# from starlette.requests import HTTPConnection
# from starlette.responses import PlainTextResponse, Response
# from starlette.types import ASGIApp, Receive, Scope, Send


# class AuthenticationMiddleware:
#     def __init__(
#         self,
#         app: ASGIApp,
#         backend: AuthenticationBackend,
#         on_error: typing.Callable[
#             [HTTPConnection, AuthenticationError], Response
#         ] = None,
#     ) -> None:
#         self.app = app
#         self.backend = backend
#         self.on_error = (
#             on_error if on_error is not None else self.default_on_error
#         )  # type: typing.Callable[[HTTPConnection, AuthenticationError], Response]

#     async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
#         if scope["type"] not in ["http", "websocket"]:
#             await self.app(scope, receive, send)
#             return

#         conn = HTTPConnection(scope)
#         try:
#             auth_result = await self.backend.authenticate(conn)
#         except AuthenticationError as exc:
#             response = self.on_error(conn, exc)
#             if scope["type"] == "websocket":
#                 await send({"type": "websocket.close", "code": 1000})
#             else:
#                 await response(scope, receive, send)
#             return

#         if auth_result is None:
#             auth_result = AuthCredentials(), UnauthenticatedUser()
#         scope["auth"], scope["user"] = auth_result
#         await self.app(scope, receive, send)

#     @staticmethod
#     def default_on_error(conn: HTTPConnection, exc: Exception) -> Response:
#         return PlainTextResponse(str(exc), status_code=400)
