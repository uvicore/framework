import uvicore
from jwt import PyJWKClient, decode
from uvicore.support.hash import md5
from uvicore.contracts import UserInfo
from uvicore.support.dumper import dump, dd
from uvicore.http.request import HTTPConnection
from uvicore.typing import Dict, Optional, Union, Callable
from uvicore.auth.authenticators.base import Authenticator
from uvicore.http.exceptions import NotAuthenticated, InvalidCredentials, HTTPException


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

    async def authenticate(self, request: HTTPConnection) -> Union[UserInfo, bool]:
        self.log.debug('JWT Authenticator')

        # Parse authorization header
        authorization, scheme, token = self.auth_header(request)

        # This authentication method not provided or attempted, goto next authenticator
        if not authorization or scheme != "bearer":
            # Return of False means this authentication method is not being attempted
            # goto next authenticator in stack
            self.log.debug('No Bearer found in Authorization header, goto next authenticator in stack')
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
            self.log.debug('Anonymous header found, this is an Anonymous request')
            return True

        #dump(request.headers)

        # Decode JWT with or without verification
        jwt = None

        # Verify JWT internally with uvicore
        if self.config.verify_signature:
            #dump('VALIDATE JWT INTERNALLY')

            # Verify JWT using JWKS
            if self.config.verify_signature_method.lower() == 'jwks':
                default_jwks_url = uvicore.config.app.auth.oauth2.base_url + uvicore.config.app.auth.oauth2.jwks_path
                found_consumer = False
                for (consumer_name, consumer) in self.config.consumers.items():
                    try:
                        # Cache decoded JWT to prevent hitting JWKS url often
                        async def query_jwks():
                            #dump('NO CACHE, TRY CONSUMER: ' + consumer_name)

                            # Get default or overridden jwks_url
                            jwks_url = consumer.jwks_url or default_jwks_url
                            self.log.debug('Verifying JWT via JWKS URL {}'.format(jwks_url))

                            # Get signing_key from jwks
                            jwks_client = PyJWKClient(jwks_url)
                            signing_key = jwks_client.get_signing_key_from_jwt(token)
                            return Dict(decode(
                                jwt=token,
                                key=signing_key.key,
                                audience=consumer.aud,
                                algorithms=consumer.algorithms
                            ))

                        # Get decoded JWT from cache or decode from JWKS URL signing_key
                        jwt = await uvicore.cache.remember(token, query_jwks, seconds=self.config.jwks_query_cache_ttl or 300)
                        found_consumer = True
                        self.log.debug('Found consumer via JWKS, name: {}, aud: {}'.format(consumer_name, consumer.aud))
                        break
                    except Exception as e:
                        # Means this one consumer loop JWK or secret not verified, OK, continue gracefully to next consumer
                        pass

                if not found_consumer:
                    self.log.debug('Could not validate JWT against any consumers vai JWKS.  Return True to denote Anonymous user and skip next authenticator')
                    return True

            # Verify JWT using pub key secrets
            else:
                self.log.debug('Verifying JWT via SECRET')
                for (consumer_name, consumer) in self.config.consumers.items():
                    try:
                        jwt = Dict(decode(
                            jwt=token,
                            key=consumer.secret,
                            audience=consumer.aud,
                            algorithms=consumer.algorithms
                        ))
                        self.log.debug('Found consumer via SECRET, name: {}, aud: {}'.format(consumer_name, consumer.aud))
                        break
                    except Exception as e:
                        self.log.debug('Issue validating JWT via SECRETS.  No valid secrets or audiences found.  Return True to denote Anonymous user and skip next authenticator')
                        self.log.debug(e)
                        return True

        # No JWT validation (should be pre-validated by external API Gateway like Kong)
        else:
            self.log.debug('External JWT verification via API Gateway is being used.  Uvicore will not validate JWT but may verify aud claims.')
            try:
                # Decode JWT without signature verification
                jwt = Dict(decode(token, options={"verify_signature": False}))

                # Validate aud claims if enabled
                if self.config.verify_audience:
                    # Get all allowed consumer audiences
                    audiences = [v['aud'] for (k,v) in self.config.consumers.items()]
                    if jwt.aud not in audiences:
                        # Audience mismatch, return True to denote Anonymous user and skip next authenticator
                        self.log.debug('No audience found in allowed consumers')
                        return True
            except Exception as e:
                self.log.debug('Issue decoding JWT without signature verification Ruturn True to denote Anonymous user and skip next authenticator')
                self.log.debug(e)
                return True

        # Dump JWT to DEBUG log
        self.log.debug('JWT: ' + str(jwt))

        # Map JWT based on our auth configs JWT authenticator auto_create_user_jwt_mapping
        mapped_jwt = {}
        for key, value in self.config.auto_create_user_jwt_mapping.items():
            if isinstance(value, Callable):
                mapped_jwt[key] = value(jwt)
            else:
                mapped_jwt[key] = value

        # Dump Mapped JWT to DEBUG log
        self.log.debug('Mapped JWT: ' + str(mapped_jwt))

        # Get user and validate credentials
        user: UserInfo = await self.retrieve_user(mapped_jwt['email'], None, self.config.provider, request, jwt=jwt)

        # User from valid JWT not found in uvicore OR not synced for first time (no uuid).
        # Auto create or update user if allowed in config
        if self.config.auto_create_user and (user is None or user.uuid is None):
            # User does not exist, create user
            if user is None:
                # Auto create new user in user provider
                await self.create_user(self.config.provider, request, **mapped_jwt)
            else:
                # User exists, but needs an initial sync
                await self.sync_user(self.config.provider, request, **mapped_jwt)

            # Re-pull user after creation
            user: UserInfo = await self.retrieve_user(mapped_jwt['email'], None, self.config.provider, request, jwt=jwt)

        # Periodically sync user and group info from JWT
        if (self.config.sync_user):
            # Example cache key mreschke.wiki::cache/users/mreschke@example.com/sync_user_ttl
            cache_key = "users/" + user.email + "/sync_user_ttl"
            cache_ttl = self.config.sync_user_ttl
            #if not await uvicore.cache.has(cache_key):
            await self.sync_user(self.config.provider, request, **mapped_jwt)
            await uvicore.cache.put(cache_key, 1, seconds=cache_ttl)

        # Return user.  If no user return True to denote Anonymous User and skip next authenticator
        return user or True
