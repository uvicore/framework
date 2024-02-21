from uvicore.configuration import env
from uvicore.typing import OrderedDict


# --------------------------------------------------------------------------
# Package Dependencies (Package Providers)
#
# Define all the packages that this package depends on.  At a minimum, only
# the uvicore.foundation package is required.  The foundation is very minimal
# and only depends on configuration, logging and the console packages. You
# must add other core services built into uvicore only if your package
# requires them.  Services like uvicore.database, uvicore.orm, uvicore.auth
# uvicore.http, etc...
# --------------------------------------------------------------------------
dependencies = OrderedDict({
        'uvicore.foundation': {
            'provider': 'uvicore.foundation.package.provider.Foundation',
        },
        'uvicore.redis': {
            'provider': 'uvicore.redis.package.provider.Redis',
        },
        'uvicore.database': {
            'provider': 'uvicore.database.package.provider.Database',
        },
        'uvicore.orm': {
            'provider': 'uvicore.orm.package.provider.Orm',
        },
        'uvicore.auth': {
            'provider': 'uvicore.auth.package.provider.Auth',
        },
        'uvicore.http': {
            'provider': 'uvicore.http.package.provider.Http',
        },
        'uvicore.http_client': {
            'provider': 'uvicore.http_client.package.provider.HttpClient',
        },
        # 'mreschke.themes': {
        #    'provider': 'mreschke.themes.package.provider.themes.Themes',
        # },
})
