from collections import OrderedDict
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
    'debug': False,


    # --------------------------------------------------------------------------
    # Uvicorn Development Server
    #
    # Configure the dev server when you run `./uvicore http serve`
    # --------------------------------------------------------------------------
    'server': {
        'app': 'app1.http.server:http',
        'host': env('SERVER_HOST', '127.0.0.1'),
        'port': env.int('SERVER_PORT', 5000),
        'reload': env.bool('SERVER_RELOAD', True),
        'access_log': env.bool('SERVER_ACCESS_LOG', True),
    },


    # --------------------------------------------------------------------------
    # OpenAPI Auto API Doc Configuration
    #
    # Configure the OpenAPI endpoints and displayed title
    # --------------------------------------------------------------------------
    'openapi': {
        'title': 'App1 API Docs',
        'url': '/openapi.json',
        'docs_url': '/docs',
        'redoc_url': '/redoc',
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
        'uvicore.auth.database.tables.users.Users': 'app1.database.tables.users.Users',
        'uvicore.auth.models.user.User': 'app1.models.user.User',
        #'uvicore.auth.database.seeders.seeders.seed': 'app1.database.seeders.seeders.seed',

        # Low level core uvicore libraries
        'uvicore.foundation.application._Application': 'app1.overrides.application.Application',
        # 'ServiceProvider': 'mreschke.wiki.overrides.provider.ServiceProvider',
        'uvicore.package.Package': 'app1.overrides.package.Package',

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


    # Add more laravel stuff, locale, timezone etc...















    # OLD STUFF

    # --------------------------------------------------------------------------
    # Inversion of Control (IoC) Concrete Implimentation Overrides
    # --------------------------------------------------------------------------
    # Many core or small classes do not use service providers at all.  But all
    # classes use the IoC for their implimentation to allow you to override
    # anything, even the smallest of classes.  Use this section to override all
    # other non service provider based classes.  If the array is empty the
    # defaults in `uvicore/container/ioc.py` are used.

    # No this is obsolete now thanks to the new bind default and make feature
    # Now even core IoC instances like Application can be overwridded by the
    # bindings array above!!!
    #NO'ioc': {
        # 'Application': {
        #     'object': 'mreschke.wiki.overrides.application.Application',
        #     'singleton': True,
        #     'aliases': ['App', 'app', 'application']
        # },
        # 'ServiceProvider': {
        #     'object': 'mreschke.wiki.overrides.provider.ServiceProvider',
        #     'aliases': ['service', 'provider'],
        # },
        # 'Package': {
        #     'object': 'mreschke.wiki.overrides.package.Package',
        #     'aliases': ['package']
        # },
    #},


}
