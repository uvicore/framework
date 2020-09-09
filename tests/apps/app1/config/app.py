from collections import OrderedDict
from uvicore.configuration import env


config = {

    # --------------------------------------------------------------------------
    # App Information
    # --------------------------------------------------------------------------
    'name': 'App1',
    'main': 'app1',
    'debug': False,


    # --------------------------------------------------------------------------
    # Uvicorn Development Server
    # --------------------------------------------------------------------------
    # This configures the dev server when you run `./uvicore http serve`
    'server': {
        'app': 'app1.http.server:http',
        'host': env('SERVER_HOST', '127.0.0.1'),
        'port': env.int('SERVER_PORT', 9863),
        'reload': env.bool('SERVER_RELOAD', True),
        'access_log': env.bool('SERVER_ACCESS_LOG', True),
    },


    # --------------------------------------------------------------------------
    # OpenAPI Auto API Doc Configuration
    # --------------------------------------------------------------------------
    'openapi': {
        'title': 'App1 API Docs',
        'url': '/openapi.json',
        'docs_url': '/docs',
        'redoc_url': '/redoc',
    },

    # --------------------------------------------------------------------------
    # Package Dependencies (Service Providers)
    # --------------------------------------------------------------------------
    # Packages add functionality to your applications.  In fact your app itself
    # is a package that can be used inside any other app.  Uvicore framework is
    # also split into packages which use services providers to inject core
    # functionality.  Order matters for override/deep merge purposes.  Each
    # package overrides items of the previous, so the last package wins.
    # Example, configs defined with the same key are deep merged with last
    # one winning. Defining your actual apps package last means it will win
    # in all override battles.
    # Overrides include: providers, configs, views, templates, assets
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
    # Service Provider Binding Definitions
    # --------------------------------------------------------------------------
    # Most service providers bind classes into the IoC.  Most uvicore framework
    # providers will lookup this array to let you override which classes they
    # actually bind into the container.  This lets you quickly override an
    # existing service provider binding without actually using the 'services'
    # array above to define your own complete service provider.  Often times
    # simply overriding the bound class is good enough.
    'bindings': {
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
    # Inversion of Control (IoC) Concrete Implimentation Overrides
    # --------------------------------------------------------------------------
    # Many core or small classes do not use service providers at all.  But all
    # classes use the IoC for their implimentation to allow you to override
    # anything, even the smallest of classes.  Use this section to override all
    # other non service provider based classes.  If the array is empty the
    # defaults in `uvicore/container/ioc.py` are used.
    'ioc': {
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
    },


    # --------------------------------------------------------------------------
    # Logging Configuration
    # --------------------------------------------------------------------------
    # The uvicore.logger packages does NOT provide its own config
    # because it needs to load super early in the bootstrap process.
    # So we define the logger config right here instead.  Tweak as needed.
    'logger': {
        'console': {
            'enabled': False,
            'level': 'WARNING',
            'colors': False,
        },
        'file': {
            'enabled': False,
            'level': 'WARNING',
            'file': '/dev/null',
        }
    },


    # Add more laravel stuff, locale, timezone etc...

}
