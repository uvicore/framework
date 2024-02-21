from uvicore.configuration import env
from uvicore.typing import OrderedDict

# --------------------------------------------------------------------------
# Provider and IOC Overrides
#
# You can override anything in uvicore thanks to the Inversion of Control
# Container (IoC).
# --------------------------------------------------------------------------
overrides = {

    # --------------------------------------------------------------------------
    # Provider Level Overrides
    #
    # Provider overrides allow you to override an entire packages provider therefore
    # injecting your own package as a replacement.
    #
    # Example
    # Shows how to override the entire uvicore.logging package.
    # 'uvicore.logging': {
    #     'provider': 'testcli.overrides.services.logging.Logging',
    # },
    # --------------------------------------------------------------------------
    'providers': {
        #
    },


    # --------------------------------------------------------------------------
    # IoC Binding Overrides
    #
    # Binding overrides allow you to override individual classes within a package
    # as opposed to the entire package (provider) above.  All classes that bind
    # themselves to the IoC (with decorators) will look to this main running
    # app config 'ioc_bindings' object for an override specification.  This is
    # the quickest and simplest way to override nearly every class in uvicore
    # and other 3rd party packages.
    #
    # Examples
    # Low level core uvicore libraries (too early to override in a service provider, must be done here)
    # 'uvicore.foundation.application.Application': 'testcli.overrides.application.Application',
    #
    # Note about ModelRouter
    # This is the only class that must be completely re-implimented, extension is NOT allowed.
    # 'uvicore.http.routing.model_router.ModelRoute': 'testcli.overrides.http.model_router.ModelRoute',
    # --------------------------------------------------------------------------
    'ioc_bindings': {
            # Examples using short alias override
            # 'Logger': 'mreschke.wiki.overrides.logger.Logger',

            # Examples using full path
            # Low level core uvicore libraries (too early to override in a service provider, must be done here)
            # 'uvicore.foundation.application.Application': 'app1.overrides.application.Application',

            # Note about ModelRouter
            # This is the only class that must be complete re-implimented, extension is NOT allowed.
            # 'uvicore.http.routing.model_router.ModelRoute': 'app1.overrides.http.model_router.ModelRoute',

            # Testing, override Users table and model
            # You can either define here, or define in service provider boot() like so:
                #self.bind_override('uvicore.auth.database.tables.users.Users', 'app1.database.tables.users.Users')
                #self.bind_override('uvicore.auth.models.user.User', 'app1.models.user.User')
            'uvicore.auth.database.tables.users.Users': 'app1.database.tables.users.Users',
            'uvicore.auth.models.user.User': 'app1.models.user.User',

            # Low level core uvicore libraries (too early to override in a service provider, must be done here)
            'uvicore.foundation.application.Application': 'app1.overrides.application.Application',
            'uvicore.package.provider.Provider': 'app1.overrides.provider.Provider',
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
}
