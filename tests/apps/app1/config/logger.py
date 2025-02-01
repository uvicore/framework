from uvicore.configuration import env
from uvicore.typing import OrderedDict



# --------------------------------------------------------------------------
# Logging Configuration
#
# The uvicore.logger packages does NOT provide its own config because it
# needs to load super early in the bootstrap process.  Do not attempt to
# override the logger config in the usual way of deep merging with the same
# config key.  This is the one and only location of logging config as it
# only applies to the running app (deep merge of all packages not needed).
# Possible levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
# --------------------------------------------------------------------------
logger = {
    'console': {
        'enabled': env.bool('LOG_CONSOLE_ENABLED', True),
        'level': env('LOG_CONSOLE_LEVEL', 'INFO'),
        'colors': env.bool('LOG_CONSOLE_COLORS', True),
        'filters': [],
        'exclude': [
            'uvicore.orm',
            #'uvicore.http',
            #'uvicore.auth',
            'aioredis',
            'aiosqlite',
            'faker.factory',
        ],
    },
    'file': {
        'enabled': env.bool('LOG_FILE_ENABLED', True),
        'level': env('LOG_FILE_LEVEL', 'INFO'),
        'file': env('LOG_FILE_PATH', '/tmp/app1.log'),
        'when': env('LOG_ROTATE_WHEN', 'midnight'),
        'interval': env.int('LOG_ROTATE_INTERVAL', 1),
        'backup_count': env.int('LOG_ROTATE_BACKUP_COUNT', 7),
        'filters': [],
        'exclude': [
            'uvicore.orm',
            #'uvicore.http',
            #'uvicore.auth',
            'aioredis',
            'aiosqlite',
            'faker.factory',
        ],
    }
}
