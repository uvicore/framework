from uvicore.configuration import env
from uvicore.typing import OrderedDict


# --------------------------------------------------------------------------
# Uvicorn Development Server
#
# Configure the dev server when you run `./uvicore http serve`
# Dev server only, in production use gunicorn or uvicorn manually
# --------------------------------------------------------------------------
server = {
    'app': 'app1.http.server:http',
    'host': env('SERVER_HOST', '127.0.0.1'),
    'port': env.int('SERVER_PORT', 5000),
    'reload': env.bool('SERVER_RELOAD', True),
    'access_log': env.bool('SERVER_ACCESS_LOG', True),
}



# --------------------------------------------------------------------------
# API HTTP Server
#
# API endpoint specific configuration and middleware.
# Middleware is fully defined from the running application only.  Packages
# Do not inject their own middleware as the running app should dictate all.
# --------------------------------------------------------------------------
api = {
    # URL prefix for all API endpoints
    'prefix': env('API_PREFIX', '/api'),

    # Page Size
    'page_size': 25, # 3
    'page_size_max': 100, # 5

    # OpenAPI docs site configuration
    'openapi': {
        'title': env('OPENAPI_TITLE', 'Wiki API Docs'),
        'path': '/openapi.json',
        'docs': {
            'path': '/docs',
            'expansion': 'list',  # list none full
            'favicon_url': 'data:image/x-icon;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQEAYAAABPYyMiAAAABmJLR0T///////8JWPfcAAAACXBIWXMAAABIAAAASABGyWs+AAAAF0lEQVRIx2NgGAWjYBSMglEwCkbBSAcACBAAAeaR9cIAAAAASUVORK5CYII=',
            'js_url': 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.7.2/swagger-ui-bundle.js',
            'css_url': 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.7.2/swagger-ui.min.css',
        },
        # If oauth2 is enabled, edit app.auth.oauth2 configuration below
        'oauth2_enabled': True,
    },

    # API exception handlers
    'exception': {
        'handler': 'uvicore.http.exceptions.handlers.api',
    },

    # API middleware
    'middleware': OrderedDict({
        # Only allow this site to be hosted from these domains
        'TrustedHost': {
            'module': 'uvicore.http.middleware.TrustedHost',
            'options': {
                # Host testserver is for automated unit tests
                'allowed_hosts': env.list('API_TRUSTED_HOSTS', ['127.0.0.1', '0.0.0.0', 'localhost', 'testserver']),
                'www_redirect': True,
            }
        },

        # Only allow these domains to access routes
        'CORS': {
            'module': 'uvicore.http.middleware.CORS',
            'options': {
                # Allow origins are full protocol://domain:port, ie: http://127.0.0.1:5000
                'allow_origins': env.list('CORS_ALLOW_ORIGINS', ['http://127.0.0.1:5000', 'http://0.0.0.0:5000', 'http://localhost:5000']),
                'allow_methods': env.list('CORS_ALLOW_METHODS', ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']),
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

    # Automatic Model CRUD API Configuration
    'auto_api': {
        # Override the automatic CRUD scopes with a List.  This sets the
        # scopes for all endpoints and verbs.  Setting to [] opens all auto
        # endpoints up to the public (no permissions).
        'scopes': [],

        # Override the automatic CRUD scopes with a Dictionary.  This sets
        # the scopes for all endpoints but taylored per HTTP verb.
        #'scopes': {
        #    'create': 'autoapi.create',
        #    'read': 'autoapi.read',
        #    'update': 'autoapi.update',
        #    'delete': 'autoapi.delete',
        #},

        # Include only these models in the auto api model router.
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

        # Exclude these models from the auto api model router.
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
}



# --------------------------------------------------------------------------
# Web HTTP Server
#
# Web endpoint specific configuration and middleware.
# Middleware is fully defined from the running application only.  Packages
# Do not inject their own middleware as the running app should dictate all.
# --------------------------------------------------------------------------
web = {
    # URL prefix for all Web endpoints
    'prefix': env('WEB_PREFIX', ''),

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

    # Web middleware
    'middleware': OrderedDict({
        # Only allow this site to be hosted from these domains
        'TrustedHost': {
            'module': 'uvicore.http.middleware.TrustedHost',
            'options': {
                # Host testserver is for automated unit tests
                'allowed_hosts': env.list('WEB_TRUSTED_HOSTS', ['127.0.0.1', '0.0.0.0', 'localhost', 'testserver']),
                'www_redirect': True,
            }
        },

        # Detect one or more authentication mechanisms and load valid or anonymous user into request.user
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
}
