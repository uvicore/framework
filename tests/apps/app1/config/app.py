from uvicore.typing import OrderedDict
from uvicore.configuration import env

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
        'asset': {
            'host': 'http://some.assetserver.com',
            'path': '/static',
        },
        'middleware': OrderedDict({
            'TrustedHost': {
                'module': 'uvicore.http.middleware.TrustedHost',
                'options': {
                    'allowed_hosts': ['127.0.0.1', 'localhost', 'sunjaro', 'uvicore-local.sunfinity.com'],
                    'www_redirect': True,
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
            'TrustedHost': {
                'module': 'uvicore.http.middleware.TrustedHost',
                'options': {
                    'allowed_hosts': ['127.0.0.1', 'localhost', 'sunjaro', 'uvicore-local.sunfinity.io'],
                    'www_redirect': True,
                }
            },
            'CORS': {
                'module': 'uvicore.http.middleware.CORS',
                'options': {
                    'allow_origins': ['127.0.0.1', 'localhost', 'sunjaro', 'uvicore-local.sunfinity.io'],
                    'allow_methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
                    'allow_headers': [],
                    'allow_credentials': False,
                    'allow_origin_regex': None,
                    'expose_headers': [],
                    'max_age': 600,
                }
            },

        }),
    },


    # --------------------------------------------------------------------------
    # Static Assets
    #
    # Leaving all blank uses the served apps host and defailt /assets path.
    # Setting only a path uses the served apps host with a custom path.
    # Setting both overrides the entire url completely.  Usefull when your
    # assets are on a separate server or being hosted from a webpack hot reload.
    # The actual folder in your package that holds these assets is defined in your
    # packages service provider in the Http mixin using self.assets() method.
    # --------------------------------------------------------------------------
    # 'asset': {
    #     'host': 'http://some.assetserver.com',
    #     'path': '/static',
    # },


    # --------------------------------------------------------------------------
    # HTTP auth guards, authenticator middleware and user providers
    #
    # Each route or controller can specify an auth guard to use.  Web and API
    # endpoints often use different guards for authentication.  Often times
    # multiple authentication methods are used.  For example, API routes may
    # authenticate using JWT Bearer tokens AND Digest Auth while web routes
    # may only use Session Auth.  Each of these authenticators has various
    # options which are generally the same when applied to multiple guards.
    # The 'options' Dict allows deep merging of default options to eliminate
    # duplication in this config.
    # --------------------------------------------------------------------------
    'auth': {
        # Default auth guard to use if none specified in route middleware (auth=Guard(guard='web'))
        'default': 'web',

        # Auth Guards with one or more authenticator middleware
        'guards': {
            'web': {
                'authenticators': {
                    'basic': {
                        # Deep merge default options from 'options' Dictionary below.
                        # Can override any default options by specifying them here
                        'options': 'basic',
                        #'return_www_authenticate_header': True,
                    }
                },
            },
            'api': {
                'authenticators': {
                    'jwt': {
                        # Deep merge default options from 'options' Dictionary below.
                        # Can override any default options by specifying them here
                        'options': 'jwt',
                    },
                    'basic': {
                        # Deep merge default options from 'options' Dictionary below.
                        # Can override any default options by specifying them here
                        'options': 'basic',
                    },
                },
            }
        },

        # User repository providers
        'providers': {
            'users': {
                'module': 'uvicore.auth.models.user.User',
                'method': 'userinfo',
                'model': 'uvicore.auth.models.user.User',
                'includes': ['roles', 'roles.permissions', 'groups', 'groups.roles', 'groups.roles.permissions'],
            },
        },

        # Authenticator default options
        'options': {
            'basic': {
                'module': 'uvicore.auth.middleware.Basic',
                'provider': 'users',
                'return_www_authenticate_header': False,
                'realm': 'App1 Realm'
            },
            'jwt': {
                'module': 'uvicore.auth.middleware.Jwt',
                'provider': 'users',

                # Settings used when there is an API gateway upstream from this API
                'api_gateway': {
                    'enabled': True,
                    'anonymous_header': 'x-anonymous-consumer',  # Set to None to skip header checks
                    #'anonymous_header': None,
                },

                # Settings used when the user auth and JWT did not originate from this app itself
                # but from an external Identity Provider
                'external_idp': {
                    'enabled': True,

                    'auto_create_user': True,
                    'sync_scopes': True,
                },
                'verify_signature': True,  # False only if a local upstream API gateway has already pre-validated
                'audience': 'd709a432-5edc-44c7-8721-4cf123473c45',  # FusionAuth App ID
                'algorithms': ['RS256'],
                #'secret': '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnc84SDViVX8JNye2GVQZ\nixAwG2PWXoOhkj++wGASoAXs2LN0Ue48conxf/0bgEtq6kcbLPR23SieqBZA77vc\nyulimMbzfwNczyP3FRo8wSCqRgJipTse87WItd8ga2MUCzSS8q19V4swUT4T23Su\nDiG/Ry5f1sYbvxP2kJAJMUCzVbS7STxh33h65Bj+P6JdzrCJi+yrLqg928RHjLIF\ngDy4MyFBLTI8w5u6IJi1TLm6h9lj3YqSa/qDkkIardnnZa7Xj0IJCEB9c+RD4Q7C\n+jco6g2Vr9oLP8Mg3c5lZPNVzcXC67UMVk9lK+zrlfPDI/m2+9kyTc/58S9ZUTFJ\nQwIDAQAB\n-----END PUBLIC KEY-----',
                'secret': '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkz3donSSkj3tcFh//cB/\nGes4H9muNlkfB93BYV3kv1p17u/18qLyeNO9dCjr+KChSr9OwqwCkSW+jqck2pvC\n2sgFQ1zg9M+eqUT9lToltbHYMs0m1vsHzDLOqiCnRUwiWeiaUfzoscz26isOR8GH\nII8TQJ+3cHPC0mGs0uBlGHxgT7bigmmKS+otFxRnYffRA+6kkp4jtkYx25tD/vDY\nSOCF3vszcnfng0w661nzCOYTqBNiw9GyIW1i2mrXAQe+pxczRWvIO1D6i0wvWEKQ\n8Dz1goA+anK7TD21g4bgXZFcw30eNezA5vHeDXemzOKEJAIv7jP6D6P/aSIdbpQo\n3QIDAQAB\n-----END PUBLIC KEY-----',
            },

        }
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
