import uvicore
from uvicore.typing import Dict, Tuple
from uvicore.http import Request
from fastapi.security import SecurityScopes
from uvicore.support.dumper import dump, dd
from uvicore.http.exceptions import HTTPException, PermissionDenied, InvalidCredentials
from uvicore.http import status
from uvicore.support import module
import jwt
from uvicore.auth.middleware.auth import Auth


@uvicore.service()
class Jwt(Auth):
    """Jwt Authentication Route Middleware"""

    def __init__(self, config: Dict):
        self.config = config

    async def __call__(self, scopes: SecurityScopes, request: Request):
        dump('JWT HERE')
        dump(scopes.__dict__, self.config)
        dump('-----------------------------------------------------------------')
        # Assume unauthorized
        authorized = False

        # Parse authorization header
        authorization, scheme, token = self.auth_header(request)

        #dump("AUTHORIZATION:", authorization)
        #dump("SCHEME", scheme)
        #dump("TOKEN", token)
        dump('HEADERS', request.headers)

        # Detect anonymous API access.
        # API gateways that allow anonymous access to an API will pass the request
        # downstream even if the token is missing, invalid or expired.
        # When they do, they add a header notifying downstream that auth has failed
        # but anonymous access is still allowed.  For Kong this header is x-anonymous-consumer
        # If the API gateway does not allow anonymous access, downstream won't even be proxied.
        if (self.config.api_gateway.enabled
            and self.config.api_gateway.anonymous_header
            and self.config.api_gateway.anonymous_header in request.headers
        ):
            # Anonymous header configured and found in headers.  This is an anonymous connection.
            # No need to check JWT, simply return anonymous "public" user.
            dump('ANONYMOUS CONNECTION, RETURN PUBLIC USER')
            return




        # Kong with NO JWT using anonymous example
        # headers
        """
        {'host': 'sunjaro:5000', 'connection': 'keep-alive',
        'x-forwarded-for': '127.0.0.1, 172.26.0.1', 'x-forwarded-proto': 'https',
        'x-forwarded-host': 'uvicore-local.sunfinity.io',
        'x-forwarded-port': '8443', 'x-real-ip': '172.26.0.1',
        'user-agent': 'HTTPie/2.4.0', 'accept-encoding': 'gzip, deflate',
        'accept': '*/*',

        # This is anonymous kong ID if x-anonymous-consumer = True
        'x-consumer-id': '1be13da8-296d-4653-bb68-cdc7f4b54a6d',
        'x-consumer-custom-id': 'anonymous',
        'x-consumer-username': 'anonymous',
        'x-anonymous-consumer': 'true'})
        """


        # Headers, Kong with valid token
        """
        {'host': 'sunjaro:5000', 'connection': 'keep-alive',
        'x-forwarded-for': '127.0.0.1, 172.26.0.1', 'x-forwarded-proto': 'https',
        'x-forwarded-host': 'uvicore-local.sunfinity.io', 'x-forwarded-port': '8443',
        'x-real-ip': '172.26.0.1', 'user-agent': 'HTTPie/2.4.0', 'accept-encoding': 'gzip, deflate',
        'accept': '*/*',
        'authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ii1GV1Z1eEg0eGh2NnhxQUV5akVfdXBfd0NiZyJ9.eyJhdWQiOiJkNzA5YTQzMi01ZWRjLTQ0YzctODcyMS00Y2YxMjM0NzNjNDUiLCJleHAiOjE2MTUzMzE0OTAsImlhdCI6MTYxNTMyNzg5MCwiaXNzIjoiaHR0cHM6Ly9hdXRoLWxvY2FsLnN1bmZpbml0eS5jb20iLCJzdWIiOiIxNGEzZjY0Yi0zNzcwLTQ1NDktOWZjNS00YjYxZmY4YjIwNzAiLCJhdXRoZW50aWNhdGlvblR5cGUiOiJQQVNTV09SRCIsImVtYWlsIjoibWFuYWdlcjFAZXhhbXBsZS5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXBwbGljYXRpb25JZCI6ImQ3MDlhNDMyLTVlZGMtNDRjNy04NzIxLTRjZjEyMzQ3M2M0NSIsInJvbGVzIjpbIkVtcGxveWVlIiwiU2FsZXMgSW50ZXJuYWwiLCJVc2VyIl0sIm5hbWUiOiJNYW5hZ2VyfE9uZSJ9.JaR8EdMdd5XdUBZuPWXm-uVghODp84LzQON3kwwshqrjR5PyAO6HP6S5wGg1Y-dKMfETkbNy5sh9RP3nZWHtwB7ZukQ3IwIrC5Ako3a1VZWFzSu1mR3_1X510DvTQVwdfWz_XvEwG5v8O01n-UrLXWQHvgKDeEs3HPkuel-kHXajhoP6oEVxXqb3AmzCIoOv9MC3_3F4jVW73FLFQA-thsVElpJiwrLlZ9ehulp-Cl92eCOS6Ug-L6aJdafx7X9Q2gTsY28cN85WVCX3dss3gJ1GO8vq8u8yIek4B-27hRtyVwaGlxKWjGPsLjE-M0VvXSqQrCIszvxlcodo1L1F5A',

        # This is kongs consumer GUID
        'x-consumer-id': '304ae0c3-de56-47dc-8c35-7c8ed7f6c08f',

        # This is the uvicore app ID
        'x-consumer-custom-id': 'd709a432-5edc-44c7-8721-4cf123473c45',
        'x-consumer-username': 'Uvicore',
        'x-credential-identifier': 'd709a432-5edc-44c7-8721-4cf123473c45'})
        """




        # This authorization method not provided or attempted, goto next guard in middleware stack
        if not authorization or scheme != "bearer":
            # Return None means goto next authenticator in authorization middleware
            return None

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
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid audience",
                    )
        except Exception as e:
            # Issue with validation.  Bad key, token expired...
            # Pass JWT library exception message right through with a generic 401
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
            )

        dump('JWT', payload)

        # {
        #     'aud': '222b06eb-85ce-472b-af30-ec09244e3bf0',
        #     'exp': 1614980706,
        #     'iat': 1614977106,
        #     'iss': 'https://auth-local.sunfinity.com',
        #     'sub': '217e27b4-0e0a-464c-84a8-c40312b55801',
        #     'authenticationType': 'PASSWORD',
        #     'email': 'it@sunfinity.com',
        #     'email_verified': True,
        #     'applicationId': '222b06eb-85ce-472b-af30-ec09244e3bf0',
        #     'roles': ['Administrator'],
        #     'name': 'Admin|Istrator'
        # }

        # Get user and validate credentials
        user = await self.retrieve_user(payload.email, None, self.config.provider)

        # If user is none and auto_create_user is enabled, auto-create user
        # Link user up to groups table based on JWT roles
        # Now self.get_user again

        # If no user returned, validation has failed or user not found
        if user is None: raise InvalidCredentials()

        # Validate Permissions
        #self.validate_permissions(user, scopes.scopes)

        # Authorization successful.
        # Add user to request in case we use it in a decorator, we can pull it out with request.scope.get('user')
        request.scope['user'] = user

        # Return user in case we are using this guard as a dependency injected route parameter
        return user

