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

        'middleware': OrderedDict({
            'TrustedHost': {
                'module': 'uvicore.http.middleware.TrustedHost',
                'options': {
                    'allowed_hosts': ['127.0.0.1', 'localhost', 'sunjaro', 'p53', 'uvicore-local.sunfinity.com'],
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
            'url': '/openapi.json',
            'docs_url': '/docs',
            'redoc_url': '/redoc',
        },
        'middleware': OrderedDict({
            # Only allow this site to be hosted from these domains
            'TrustedHost': {
                'module': 'uvicore.http.middleware.TrustedHost',
                'options': {
                    'allowed_hosts': ['127.0.0.1', 'localhost', 'sunjaro', 'p53', 'uvicore-local.sunfinity.io'],
                    'www_redirect': True,
                }
            },

            # Only allow these domains to access routes
            'CORS': {
                'module': 'uvicore.http.middleware.CORS',
                'options': {
                    'allow_origins': ['127.0.0.1', 'localhost', 'sunjaro', 'p53', 'uvicore-local.sunfinity.io'],
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
                # but from an external Identity Provider
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
                # Sync users scopes (rules/groups) form JWT with user provider
                # Does not sync on every request but is buffered with the default cache TTL seconds.
                'sync_scopes': True,

                # JWT Validation
                'verify_signature': False,  # False only if a local upstream API gateway has already pre-validated
                'audience': 'd709a432-5edc-44c7-8721-4cf123473c45',  # FusionAuth App ID
                'algorithms': ['RS256'],

                # Secret for sunjaro
                'secret': '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkz3donSSkj3tcFh//cB/\nGes4H9muNlkfB93BYV3kv1p17u/18qLyeNO9dCjr+KChSr9OwqwCkSW+jqck2pvC\n2sgFQ1zg9M+eqUT9lToltbHYMs0m1vsHzDLOqiCnRUwiWeiaUfzoscz26isOR8GH\nII8TQJ+3cHPC0mGs0uBlGHxgT7bigmmKS+otFxRnYffRA+6kkp4jtkYx25tD/vDY\nSOCF3vszcnfng0w661nzCOYTqBNiw9GyIW1i2mrXAQe+pxczRWvIO1D6i0wvWEKQ\n8Dz1goA+anK7TD21g4bgXZFcw30eNezA5vHeDXemzOKEJAIv7jP6D6P/aSIdbpQo\n3QIDAQAB\n-----END PUBLIC KEY-----',

                # Secret for p53
                #'secret': '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1ohyYNWDXOA6follmvIX\n034k5IWFLlgpwq7CA+IxFSGpnzRpOlL/22oQ/SbH4PmofWKs9qPYeRl8md5XRZus\nO+Ed8tHi7Ltz7Cjl42xX27bTLN1dqVgbecbfcUiWKlYQt1CrbNda6rCXBOx3whYQ\nfZz8G1yn7I4x55lIa14ojzRdXW7oMcJeKGdS7BPeqQ3rsreLYyk3OMwZEzq7JPXa\nxl9NuSCVEhcDgW+nHua4AauKG/JnkXRExiR65g6hINQyVYk7I6HOLTNVYZQcg/Rf\nQ84HuW6N8bgsrULkm7+KVvACsZRgdrO2ewr7ZMXpW2tbaq2GqgUNNeoZCP7EQgQZ\nEwIDAQAB\n-----END PUBLIC KEY-----',
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
        #'uvicore.auth.database.tables.users.Users': 'app1.database.tables.users.Users',
        #'uvicore.auth.models.user.User': 'app1.models.user.User',
        #'uvicore.auth.database.seeders.seeders.seed': 'app1.database.seeders.seeders.seed',

        # Low level core uvicore libraries (too early to override in a service provider, must be done here)

        # FIXME, broken with new SuperDict
        #'uvicore.foundation.application.Application': 'app1.overrides.application.Application',
        #'uvicore.package.provider.ServiceProvider': 'app1.overrides.provider.ServiceProvider',
        #'uvicore.package.package.Package': 'app1.overrides.package.Package',

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
        'default': 'mailgun',
        'mailers': {
            'mailgun': {
                'driver': 'uvicore.mail.backends.Mailgun',
                'domain': 'mailgun.mreschke.com',
                'secret': 'key-843583a6f69b92f97875d2d87c90446e',
            },
            'smtp': {
                'driver': 'uvicore.mail.backends.smtp',
                'server': 'smtp.mailgun.org',
                'port': 587,
                'username': 'postmaster@mailgun.mreschke.com',
                'password': 'ab7ea4733831a7166e449601386db487-aa4b0867-be75493f',
                'ssl': False,
            }
        },
        'from_name': 'Uvicore Test App1',
        'from_address': 'uvicore@mreschke.com',
    },


    # --------------------------------------------------------------------------
    # Cache Configuration
    # --------------------------------------------------------------------------
    'cache': {
        'default': 'redis',
        'stores': {
            # 'array': {
            #     'driver': 'uvicore.cache.backend.Array',
            # }
            'redis': {
                'driver': 'uvicore.cache.backends.Redis',
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
            'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
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
