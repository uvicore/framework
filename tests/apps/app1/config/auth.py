from uvicore.configuration import env
from uvicore.typing import OrderedDict


# --------------------------------------------------------------------------
# HTTP Authentication Middleware Configuration
#
# Both web and api routes can have their own authentication middleware.
# Configuration for each is provided below in the 'web' and 'api' sections.
# Multiple authenticators may be used.  For example, API routes may
# authenticate using JWT, Digest or Basic auth while web routes may
# only authenticate with Session and/or JWT. Each of these authenticators
# has various options and user providers which are generally the same when
# applied to multiple authenticators. The 'default_options' and 'providers'
# Dict allows deep merging of default options to eliminate config duplication.
# --------------------------------------------------------------------------
auth = {

    # Oauth2 configuration
    # Mainly used for OpenAPI doc authentication if app.api.openapi.oauth2_enabled=True
    # but may be used elsewhere in your app if needed.
    'oauth2': {
        'client_id': env('AUTH_OAUTH2_CLIENT_ID', 'xyz'),
        'base_url': env('AUTH_OAUTH2_BASE_URL', 'https://my_fusionauth_gluu_keycloke_auth0_okta.com'),
        'authorize_path': env('AUTH_OAUTH2_AUTHORIZE_PATH', '/oauth2/authorize'),
        'token_path': env('AUTH_OAUTH2_TOKEN_PATH', '/oauth2/token'),
        'jwks_path': env('AUTH_OAUTH2_JWKS_PATH', '/.well-known/jwks.json'),
    },

    # Web route authenticators and user providers
    'web': {
        # Default provider used for anonymous retrieval and for authenticators that do not specify their own
        'default_provider': 'user_model',

        # Unauthenticated handler
        'unauthenticated_handler': {
            # If redirect defined, redirect to this URL on authentication or authorization failures.
            # If '/' found in redirect it will use the redirect as a URL.  If no / and a . is found
            # it will be used as a route name.  Referer ?referer=page automatically added
            'redirect': 'app1.login',

            # If no redirect defined a PermissionDenied or NotAuthenticated exception is thrown
            # You can specify custom headers to be thwon with those exceptions.  Useful for Basic Auth
            # WWW-Authenticate headers to prompt a brower based login prompt.
            'exception': {
                'headers': {
                    'WWW-Authenticate': 'Basic realm="App1 Web Realm"'
                },
            },
        },

        # Authenticators, multiples allow many forms of authentication
        'authenticators': {
            # 'jwt': {
            #     # Deep merge default options from 'options' Dictionary below.
            #     # Can override any default options by specifying them here
            #     'default_options': 'jwt',
            # },

            'basic': {
                # Deep merge default options from 'options' Dictionary below.
                # Can override any default options by specifying them here
                'default_options': 'basic',
            },
        },
    },

    # Api route authenticators and user providers
    'api': {
        # Default provider used for anonymous retrieval and for authenticators that do not specify their own
        'default_provider': 'user_model',

        # Authenticators, multiples allow many forms of authentication
        'authenticators': {
            'jwt': {
                # Deep merge default options from 'options' Dictionary below.
                # Can override any default options by specifying them here
                'default_options': 'jwt',
                #'provider': 'jwt',
            },
            'basic': {
                # Deep merge default options from 'options' Dictionary below.
                # Can override any default options by specifying them here
                'default_options': 'basic',
            },
        },
    },

    # User repository providers
    'providers': {
        'user_model': {
            'module': 'uvicore.auth.user_providers.Orm',
            # Options are passed as parameters into the UserProvider retrieve methods
            'options': {
                'includes': ['roles', 'roles.permissions', 'groups', 'groups.roles', 'groups.roles.permissions'],
            },
            # Anonymous options are MERGED with options to get the anonymous user only with not authenticated
            'anonymous_options': {
                'username': 'anonymous',
                'anonymous': True,
            },
        },
        'jwt': {
            'module': 'uvicore.auth.user_providers.Jwt',
            'options': {
                # Map JWT keys into User attrributes. User to build user object from JWT.
                'jwt_mapping': {
                    # FusionAuth JWT Mappings
                    'id': lambda jwt: jwt['sub'],
                    'uuid': lambda jwt: jwt['sub'],
                    'username': lambda jwt: jwt['email'],
                    'email': lambda jwt: jwt['email'],
                    'first_name': lambda jwt: jwt['name'].split('|')[0],
                    'last_name': lambda jwt: jwt['name'].split('|')[1],
                    'roles': lambda jwt: jwt['roles'],
                    'permissions': lambda jwt: jwt['roles'],
                    'superadmin': lambda jwt: 'Administrator' in jwt['roles'],
                },
                # If role_permission_map is defined, map user 'permissions' into
                # user 'roles' matching these rules Dictionary.  Used for stateless static
                # User roles (from JWT) to user permission mapping.
                'role_permission_map': {
                    'Anonymous': [
                        'anonymous',
                    ],
                    'Employee': [
                        'posts.read',
                    ],
                },
            },
            # If user is not logged in, use these options in the user provider retrieve methods
            'anonymous_options': {
                'anonymous': True,
                'username': 'anonymous',
                'anonymous_user': {
                    'id': 1,
                    'uuid': 'anon-from-config',
                    'username': 'anonymous',
                    'email': 'anonymous@example.com',
                    'first_name': 'Anonymous',
                    'last_name': 'User',
                    'title': 'Anonymous',
                    'avatar': '',
                    'groups': [],
                    'roles': ['Anonymous'],
                    'permissions': [],
                    'superadmin': False,
                }
            },
        },
    },

    # Authenticator default options
    'default_options': {
        'basic': {
            #'module': 'uvicore.auth.middleware.Basic',
            'module': 'uvicore.auth.authenticators.Basic',
            #'provider': 'user_model',  # Or use the default_provider
            'return_www_authenticate_header': True,
        },
        'jwt': {
            'module': 'uvicore.auth.authenticators.Jwt',
            #'provider': 'user_model',  # Or use the default_provider

            # Settings used when there is an API gateway upstream from this API
            'anonymous_header': 'x-anonymous-consumer',  # Set to None to skip header checks

            # Settings used when the user auth and JWT did not originate from this app itself
            # but from an external Identity Provider. We want to create and sync the external IDP
            # user to uvicore's internal user/group/roles tables.
            'auto_create_user': True,
            'auto_create_user_jwt_mapping': {
                # FusionAuth JWT Mappings
                'uuid': lambda jwt: jwt['sub'],
                'username': lambda jwt: jwt['email'],
                'email': lambda jwt: jwt['email'],
                'first_name': lambda jwt: jwt['name'].split('|')[0],
                'last_name': lambda jwt: jwt['name'].split('|')[1],
                'title': '',
                'avatar': '',
                'creator_id': 1,
                'groups': lambda jwt: jwt['roles'],
            },

            # Periodically sync user info, roles and groups from the JWT
            # Does not sync on every request but is buffered with the TTL seconds.
            'sync_user': True,
            'sync_user_ttl': env.int('API_JWT_SYNC_USER_TTL', 600),

            # Validate JWT Signature
            # Set to False only if an upstream API gateway (like Kong) has already pre-validated the JWT
            'verify_signature': env.bool('API_JWT_VERIFY_SIGNATURE', True),
            'verify_signature_method': env('API_JWT_VERIFY_SIGNATURE_METHOD', 'secret'),  # secret, jwks
            'jwks_query_cache_ttl': env.int('API_JWT_JWKS_QUERY_CACHE_TTL', 300),

            # Validate JWT audience (aud) claim
            # Set to False only if an upstream API gateway (like Kong) has already pre-validated the JWT
            # Only applies if verify_signature is False, uvicore may still verify audience.
            'verify_audience': env.bool('API_JWT_VERIFY_AUDIENCE', True),

            # Allowed consumers
            # List of all oauth2 consumers allowed to access this API.  Verification only performed
            # by uvicore if 'verify_signature' is True.  Verification method can be direct secret or
            # jwks lookups.  If 'verify_signature' if False, but 'verify_audience' is true
            # this dictionary only needs the 'aud' keys defined.
            'consumers': {
                # 'web-app1': {
                #     'aud': 'appId, clientId, aud claim',
                #     #'jwks_url': 'optional override per consumer from default in oauth2 config above',
                #     'algorithms': ['RS256'],
                #     'secret': env('API_JWT_CONSUMER_WEB_APP1_SECRET', 'begin public key...used if method is secret'),
                # },
            },
        },
    },
}
