from uvicore.configuration import env
from uvicore.typing import OrderedDict


# --------------------------------------------------------------------------
# Cache Configuration
#
# Uvicore allows for multiple cache stores ( backends) like redis and array.
# Use 'default' to set the default backend.  The 'connection' property ties
# back to a config/database.py redis connection store name. If no cache
# config defined, the default of 'array' caching will be used
# --------------------------------------------------------------------------
cache = {
    'default': env('CACHE_STORE', 'array'),  # redis, array
    'stores': {
        'redis': {
            'driver': 'uvicore.cache.backends.redis.Redis',
            'connection': 'cache',
            'prefix': env('CACHE_PREFIX', 'app1::cache/'),
            'seconds': env.int('CACHE_EXPIRE', 600),  # 0=forever
        },
    },
}
