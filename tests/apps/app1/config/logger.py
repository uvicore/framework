from uvicore.configuration import env



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
            'asyncio',
            'aioredis',
            'aiosqlite',
            'faker.factory',
        ],
    },
    'file': {
        'enabled': env.bool('LOG_FILE_ENABLED', True),
        'level': env('LOG_FILE_LEVEL', 'INFO'),

        # This app deliberately uses a STATIC filename so the test suite keeps
        # covering the legacy TimedRotatingFileHandler path.  Put strftime tokens
        # in here (see the schematic app config) to get date stamped filenames
        # instead - '/tmp/%Y-%m-%d_{channel}.log' - which never rename anything.
        'file': env('LOG_FILE_PATH', '/tmp/app1.log'),

        # Days to keep dated log files, 0 = keep forever.  Only applies to dated
        # filenames; a static filename uses backup_count below instead.
        'retention': env.int('LOG_FILE_RETENTION', 0),

        # Legacy rotation, used ONLY when 'file' above has no strftime tokens
        'when': env('LOG_ROTATE_WHEN', 'midnight'),
        'interval': env.int('LOG_ROTATE_INTERVAL', 1),
        'backup_count': env.int('LOG_ROTATE_BACKUP_COUNT', 7),

        'filters': [],
        'exclude': [
            'uvicore.orm',
            #'uvicore.http',
            #'uvicore.auth',
            'asyncio',
            'aioredis',
            'aiosqlite',
            'faker.factory',
        ],
    },

    # --------------------------------------------------------------------------
    # Named log channels
    #
    # Each channel gets its OWN log file and its own python logger, which is how
    # one app gives each of its features/sections a separate log:
    #
    #   uvicore.log.channel('Processor').info('batch complete')
    #
    # A channel inherits the console/file config above (except filters/exclude)
    # so an empty {} is usually all you need.  Combined with a dated
    # '%Y-%m-%d_{channel}.log' path that yields 2026-07-29_Processor.log.
    # --------------------------------------------------------------------------
    'channels': {
        'Auditor': {},
        'Importer': {},
        'Processor': {},

        # A channel can override anything it inherits
        'Quiet': {
            'console': {'enabled': False},  # file only, no console noise
        },
    },
}
