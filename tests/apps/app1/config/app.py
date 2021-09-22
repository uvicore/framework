from uvicore.typing import OrderedDict
from uvicore.configuration import env

# Running application configuration.
# This config only applies if this package is running as the main application.
# Accessible at config('app')

config = {

    # --------------------------------------------------------------------------
    # App Information
    #
    # name: The human readable name of this package/app.  Like 'Matts Wiki'
    # main: The package name to run when this app is served/executed
    # --------------------------------------------------------------------------
    'name': 'App1',
    'main': 'app1',
    'debug': True,


    # --------------------------------------------------------------------------
    # Uvicorn Development Server
    #
    # Configure the dev server when you run `./uvicore http serve`
    # Dev server only, in production use gunicorn or uvicorn manually
    # --------------------------------------------------------------------------
    'server': {
        'app': 'app1.http.server:http',
        'host': env('SERVER_HOST', '0.0.0.0'),
        'port': env.int('SERVER_PORT', 5000),
        'reload': env.bool('SERVER_RELOAD', True),
        'access_log': env.bool('SERVER_ACCESS_LOG', True),
    },


    # --------------------------------------------------------------------------
    # Web HTTP Server
    #
    # Web endpoint specific configuration and middleware
    # Middleware is fully defined from the running application only.  Packages
    # Do not define their own middleware as the running app should dictate all.
    # --------------------------------------------------------------------------
    'web': {
        'prefix': '',

        # Static Assets
        # Leaving all blank uses the served apps host and defailt /assets path.
        # Setting only a path uses the served apps host with a custom path.
        # Setting both overrides the entire url completely.  Usefull when your
        # assets are on a separate server or being hosted from a webpack hot reload.
        # The actual folder in your package that holds these assets is defined in your
        # packages service provider in the Http mixin using self.assets() method.
        'asset': {
            'host': env('ASSET_HOST', None),
            'path': env('ASSET_PATH', '/assets'),
        },

        # Web exception handlers
        'exception': {
            'handler': 'uvicore.http.exceptions.handlers.web'
        },
        # 'exceptions': {
        #     'main': 'uvicore.http.exceptions.handlers.web',
        #     #404: 'uvicore.http.exceptions.handlers.handle_404',
        # },


        # Web middleware
        'middleware': OrderedDict({
            'TrustedHost': {
                'module': 'uvicore.http.middleware.TrustedHost',
                'options': {
                    # Host testserver is for automated unit tests
                    'allowed_hosts': ['127.0.0.1', 'localhost', '0.0.0.0', 'testserver', 'sunjaro', 'p53', 'uvicore-local.sunfinity.com'],
                    'www_redirect': True,
                }
            },
            'Authentication': {
                # All options are configured in the 'auth' section of this app config
                'module': 'uvicore.http.middleware.Authentication',
                'options': {
                    'route_type': 'web',  # web or api only
                }
            },

            # If you have a loadbalancer with SSL termination in front of your web
            # app, don't use this redirection to enforce HTTPS as it is always HTTP internally.
            # 'HTTPSRedirect': {
            #     'module': 'uvicore.http.middleware.HTTPSRedirect',
            # },
            # Not needed if your loadbalancer or web server handles gzip itself.
            # 'GZip': {
            #     'module': 'uvicore.http.middleware.Gzip',
            #     'options': {
            #         # Do not GZip responses that are smaller than this minimum size in bytes. Defaults to 500
            #         'minimum_size': 500
            #     }
            # },
        }),
    },


    # --------------------------------------------------------------------------
    # API HTTP Server
    #
    # API endpoint specific configuration and middleware
    # --------------------------------------------------------------------------
    'api': {
        'prefix': '/api',
        'openapi': {
            'title': 'App1 API Docs',
            'path': '/openapi.json',
            'docs': {
                'path': '/docs',
                'expansion': 'none',  # list none full
                'favicon_url': 'data:image/x-icon;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQEAYAAABPYyMiAAAABmJLR0T///////8JWPfcAAAACXBIWXMAAABIAAAASABGyWs+AAAAF0lEQVRIx2NgGAWjYBSMglEwCkbBSAcACBAAAeaR9cIAAAAASUVORK5CYII=',
                'js_url': 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.47.1/swagger-ui-bundle.js',
                'css_url': 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.47.1/swagger-ui.min.css',
            },
            # If oauth2 is enabled, edit app.auth.oauth2 configuration below
            'oauth2_enabled': True,
        },

        # API exception handlers
        'exception': {
            'handler': 'uvicore.http.exceptions.handlers.api',
        },
        #'exceptions': {
        # 'exceptions': {
        #     'main': 'uvicore.http.exceptions.handlers.api',
        #     404: 'uvicore.http.exceptions.handlers.handle_404',
        # },

        # API middleware
        'middleware': OrderedDict({
            # Only allow this site to be hosted from these domains
            'TrustedHost': {
                'module': 'uvicore.http.middleware.TrustedHost',
                'options': {
                    # Host testserver is for automated unit tests
                    'allowed_hosts': ['127.0.0.1', 'localhost', '0.0.0.0', 'testserver', 'sunjaro', 'p53', 'uvicore-local.sunfinity.io'],
                    'www_redirect': True,
                }
            },

            # Only allow these domains to access routes
            'CORS': {
                'module': 'uvicore.http.middleware.CORS',
                'options': {
                    'allow_origins': ['http://127.0.0.1:5000', 'http://0.0.0.0:5000', 'http://localhost:5000', 'sunjaro', 'p53', 'uvicore-local.sunfinity.io'],
                    #'allow_origins': ['*'],
                    'allow_methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
                    'allow_headers': [],
                    'allow_credentials': False,
                    'allow_origin_regex': None,
                    'expose_headers': [],
                    'max_age': 600,
                }
            },

            # Detect one or more authentication mechanisms and load valid or anonymous user into request.user
            'Authentication': {
                # All options are configured in the 'auth' section of this app config
                'module': 'uvicore.http.middleware.Authentication',
                'options': {
                    'route_type': 'api',  # web or api only
                }
            },
        }),

        # Automatic Model CRUD Api Configuration
        'auto_api': {
            # This app1 is used in unit tests, and those require autoapi to be WIDE OPEN

            # Set List of scopes for all endpoints and verbs
            'scopes': [],

            # Set Dict of scopes for all endpints, but different for each verb
            # 'scopes': {
            #     'create': 'autoapi.create',
            #     'read': 'autoapi.read',
            #     'update': 'autoapi.update',
            #     'delete': 'autoapi.delete',
            # },

            # Include only these models
            # Accepts wildcards, *.models.user.User because if a model is
            # overridden in another package, we still want to find that model.
            'include': [
                #'app1.models.hashtag.Hashtag'
                #'app1.models.*'
                #'*.models.hashtag.*',
                #'*.models.attribute.*',
                #'*.models.tag.*',
                #'app1.models.tag.Tag',
            ],

            # Exclude these models
            # Accepts wildcards, *.models.user.User because if a model is
            # overridden in another package, we still want to find that model.
            'exclude': [
                #'app1.models.attribute.Attribute',
                #'*.models.attribute.Attribute',
                #'uvicore.auth.models.group.Group'
                #'*.models.tag.*',
                #'uvicore.auth.*',
                #'*.models.user_info.*',
                #'*.models.user.*',
            ],
        },

    },


    # --------------------------------------------------------------------------
    # HTTP Authentication Middleware Configuration
    #
    # Both web and api routes can have their own authentication middleware.
    # Configuration for each is provided below in the 'web' and 'api' sections.
    # Multiple authenticators may be used.  For example, API routes may
    # authenticate using JWT, Digest or Basic auth while web routes may
    # only authenticate with Session auth. Each of these authenticators has
    # various options and user providers which are generally the same when
    # applied to multiple authenticators. The 'default_options' and 'providers'
    # Dict allows deep merging of default options to eliminate config duplication.
    # --------------------------------------------------------------------------
    'auth': {

        # Oauth2 configuration
        # Mainly used for OpenAPI doc authentication if app.api.openapi.oauth2_enabled=True
        # but may be used elsewhere in your app if needed.
        'oauth2': {
            'client_id': env('AUTH_OAUTH2_CLIENT_ID', 'xyz'),
            'base_url': env('AUTH_OAUTH2_BASE_URL', 'https://my_fusionauth_gluu_keycloke_auth0_okta.com'),
            'authorize_path': env('AUTH_OAUTH2_AUTHORIZE_URI', '/oauth2/authorize'),
            'token_path': env('AUTH_OAUTH2_TOKEN_URI', '/oauth2/token'),
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
                            'posts.read',
                        ],
                        'Employee': [
                            'posts.read',
                        ],
                    },
                },
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

    },


    # --------------------------------------------------------------------------
    # Package Dependencies (Service Providers)
    #
    # Packages add functionality to your applications.  In fact your app itself
    # is a package that can be used inside any other app.  Internally, Uvicore
    # framework itself is split into many packages (Config, Event, ORM, Database,
    # HTTP, Logging, etc...) which use services providers to inject the desired
    # functionality.  Always build your packages as if they were going to be
    # used as a library in someone elses app/package.  Uvicore is built for
    # modularity where all apps are packages and all packages are apps.
    #
    # Order matters for override/deep merge purposes.  Each package overrides
    # items of the previous, so the last package wins. Example, configs defined
    # in a provider with the same config key are deep merged, last one wins.
    # Defining your actual apps package last means it will win in all override
    # battles.
    #
    # If your packages relys on other packages on its own, don't define those
    # dependencies here.  Define your packages dependencnes in its package.py
    # config file instead.  This is a list of all root packages your app relies
    # on, not every dependency of those packages.
    #
    # If you want to override some classes inside any package, but not the
    # entire package provider itself, best to use the quick and easy 'bindings'
    # dictionary below.
    #
    # Overrides include: providers, configs, views, templates, assets and more
    # --------------------------------------------------------------------------
    'packages': OrderedDict({
        # Application Service Providers
        'app1': {
            'provider': 'app1.services.app1.App1',
        },
        # Overrides to service providers used must come after all packages.

        # EXAMPLE.  You can override any service provider by simply providing
        # your own provider with the same key.  To override the logger you have
        # two options.  Either override the entire service provider with your
        # own like this.  Or use the 'bindings' array below to override just the
        # class that is used in the original uvicore logging service provider.
        # 'uvicore.logging': {
        #     'provider': 'mreschke.wiki.overrides.services.logging.Logging',
        # },

        # # Example
        # 'uvicore.console': {
        #     'provider': 'mreschke.wiki.overrides.services.console.Console',
        # },
    }),


    # --------------------------------------------------------------------------
    # IoC Binding Overrides
    #
    # All classes that bind themselves to the IoC will look to the main running
    # apps 'bindings' config dictionary for an override location.  This is the
    # quickest and simplest way to override nearly every class in uvicore
    # and other 3rd party packages (assuming they are using the IoC correctly).
    # --------------------------------------------------------------------------
    'bindings': {
        # Testing, override Users table and model
        # You can either define here, or define in service provider boot() like so:
            #self.bind_override('uvicore.auth.database.tables.users.Users', 'app1.database.tables.users.Users')
            #self.bind_override('uvicore.auth.models.user.User', 'app1.models.user.User')
        'uvicore.auth.database.tables.users.Users': 'app1.database.tables.users.Users',
        'uvicore.auth.models.user.User': 'app1.models.user.User',

        # Low level core uvicore libraries (too early to override in a service provider, must be done here)
        'uvicore.foundation.application.Application': 'app1.overrides.application.Application',
        'uvicore.package.provider.ServiceProvider': 'app1.overrides.provider.ServiceProvider',
        'uvicore.package.package.Package': 'app1.overrides.package.Package',

        # This is the only class that must be complete re-implimented, extension is NOT allowed.
        #'uvicore.http.routing.model_router.ModelRoute': 'app1.overrides.http.model_router.ModelRoute',

        # Higher level uvicore libraries
        # 'Logger': 'mreschke.wiki.overrides.logger.Logger',
        # 'Configuration': 'mreschke.wiki.overrides.configuration.Configuration',
        # 'Console': 'mreschke.wiki.overrides.console.cli',
        # 'Http': 'mreschke.wiki.overrides.server.Server',
        # 'WebRouter': 'mreschke.wiki.overrides.web_router.WebRouter',
        # 'ApiRouter': 'mreschke.wiki.overrides.api_router.ApiRouter',
        # 'Routes': 'mreschke.wiki.overrides.routes.Routes',
        # 'StaticFiles': 'mreschke.wiki.overrides.static.StaticFiles',
        # 'Templates': 'mreschke.wiki.overrides.templates.Templates',
    },


    # --------------------------------------------------------------------------
    # Path Overrides
    #
    # Override the default paths for your packages items (views, models,
    # tables, routes...).  All paths relative to your uvicore packages
    # PYTHON module root, not the actual package root. If item is not defined,
    # defaults will be assumed.
    # --------------------------------------------------------------------------
    'paths': {
        #
    },


    # --------------------------------------------------------------------------
    # Mail Configuration
    # --------------------------------------------------------------------------
    'mail': {
        'default': env('MAIL_DRIVER', 'mailgun'),
        'mailers': {
            'mailgun': {
                'driver': 'uvicore.mail.backends.Mailgun',
                'domain': env('MAIL_MAILGUN_DOMAIN', ''),
                'secret': env('MAIL_MAILGUN_SECRET', ''),
            },
            'smtp': {
                'driver': 'uvicore.mail.backends.smtp',
                'server': env('MAIL_SMTP_SERVER', ''),
                'port': env.int('MAIL_SMTP_PORT', 587),
                'username': env('MAIL_SMTP_USERNAME', ''),
                'password': env('MAIL_SMTP_PASSWORD', ''),
                'ssl': env.bool('MAIL_SMTP_SSL', False),
            }
        },
        'from_name': env('MAIL_FROM_NAME', 'Uvicore'),
        'from_address': env('MAIL_FROM_ADDRESS', 'uvicore@example.com'),
    },


    # --------------------------------------------------------------------------
    # Cache Configuration
    # If no cache config defined, the default of 'array' caching will be used
    # --------------------------------------------------------------------------
    'cache': {
        'default': 'array',
        'stores': {
            'redis': {
                'driver': 'uvicore.cache.backends.redis.Redis',
                'connection': 'cache',
                'prefix': 'app1::cache/',
                'seconds': 10,  # 0=forever
            },
        },
    },


    # --------------------------------------------------------------------------
    # Logging Configuration
    #
    # The uvicore.logger packages does NOT provide its own config because it
    # needs to load super early in the bootstrap process.  Do not attempt to
    # override the logger config in the usual way of deep merging with the same
    # config key.  This is the one and only location of logging config as it
    # only applies to the running app (deep merge of all packages not needed).
    # --------------------------------------------------------------------------
    'logger': {
        'console': {
            'enabled': True,
            'level': 'DEBUG',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
            'colors': True,
            'filters': [],
            #'filters': ['root', 'uvicore'],
            #'filters': ['root', 'databases', 'uvicore.orm'],
            'exclude': [
                'uvicore',
                'databases',
            ],
        },
        'file': {
            'enabled': False,
            'level': 'DEBUG',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
            'file': '/tmp/app1.log',
            #'when': 'midnight',
            #'interval': 1,
            #'backup_count': 7,
            'filters': [],
            'exclude': [],
        }
    },


    # --------------------------------------------------------------------------
    # Pretty Printer Configuration
    #
    # Default width if not defined is 120
    # --------------------------------------------------------------------------
    # 'dump': {
    #     'width': 150
    # },

}
