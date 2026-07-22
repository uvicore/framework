from __future__ import annotations

import sys
import uvicore
import logging
import logging.config
from logging import Logger as PythonLogger
from rich.rule import Rule
from rich.text import Text
from rich.theme import Theme
from rich.console import Console
from uvicore.support.dumper import dump, dd
from uvicore.contracts import Logger as LoggerInterface


class OutputFilter(logging.Filter):
    """Python logging custom filter class"""

    def __init__(self, filters, excludes):
        self.filters = filters
        self.excludes = excludes
        super().__init__(name='')

    def filter(self, record):
        # Not an exact filter match but a contains match.  This matches how default python
        # logging filters are.  So you can filter on A.B and it will include
        # names of A.B.C and up.
        show = False
        if self.filters:
            for f in self.filters:
                if record.name[0:len(f)] == f:
                    show = True
                    break
        else:
            show = True

        if show and self.excludes:
            for exclude in self.excludes:
                if record.name[0:len(exclude)] == exclude:
                    show = False
                    break

        return show



class ExcludeFilter(logging.Filter):
    """Python logging custom exclude filter class"""

    def __init__(self, excludes):
        self.excludes = excludes
        super().__init__(name='exclude')

    def filter(self, record):
        # Not an exact filter match but a contains match.  This matches how default python
        # logging filters are.  So you can filter on A.B and it will include
        # names of A.B.C and up.
        for exclude in self.excludes:
            if record.name[0:len(exclude)] == exclude: return False
        return True


# Rich styles for the console (STDOUT/STDERR) output only.
# This theme controls every color/decoration you see on the console.  It does
# NOT affect the file handler (which stays plain %(asctime)s ... %(message)s so
# logs remain greppable), nor prettyprinter dump()/dd() output.
# Tweak these to re-skin the console.  See https://rich.readthedocs.io/en/stable/style.html
UVICORE_LOG_THEME = Theme({
    # Level styling (the whole line is styled for these levels)
    'log.debug':        'grey42',
    'log.debug.icon':   'grey42',
    'log.info':         'default',
    'log.notice':       'bold gold1',
    'log.notice.label': 'bold black on gold1',
    'log.warning':      'bold orange1',
    'log.warning.icon': 'bold orange1',
    'log.error':        'bold red1',
    'log.error.icon':   'bold red1',
    'log.critical':     'bold red1',
    'log.critical.label': 'bold white on red3',

    # Separator / line rules
    'log.rule':         'dark_orange',

    # header()  ::  ->  full width rule with centered title
    'header.rule':      'dark_orange',
    'header.title':     'bold spring_green2',

    # header2()  ##  ->  full width rule with centered title
    'header2.rule':     'grey42',
    'header2.title':    'bold cyan',

    # header3()  ===  ->  inline styled text
    'header3.mark':     'bold dark_orange',
    'header3.title':    'bold spring_green2',

    # header4()  ----  ->  inline styled text
    'header4.mark':     'bold dark_orange',
    'header4.title':    'green',

    # item()/item2()/item3()/item4()  ->  colored glyph + text
    'item.mark':        'bold green',
    'item2.mark':       'bold red',
    'item3.mark':       'bold cyan',
    'item4.mark':       'bold magenta',
    'item.text':        'bold white',
})

# NOTICE is a custom log level sitting between INFO (20) and WARNING (30).
# Registering it with the stdlib means the file handler's %(levelname)s column
# renders "NOTICE" (instead of "INFO") and level based filtering/config works.
NOTICE = 25
logging.addLevelName(NOTICE, 'NOTICE')

# Glyphs used for item tiers and status prefixes on the console.  Purely
# cosmetic (console only) - the file handler still logs the raw '* - + >'
# prefixes so log files stay plain and greppable.
ITEM_GLYPHS = {'* ': '●', '- ': '◆', '+ ': '✚', '> ': '▸'}
NOTICE_GLYPH = 'ℹ'
WARNING_GLYPH = '⚠'
ERROR_GLYPH = '✖'
DEBUG_GLYPH = '⚙'


class RichConsoleHandler(logging.Handler):
    """Rich powered console log handler.

    Replaces the old `colored` based ColoredFormatter for all STDOUT/STDERR
    console output.  It keeps the exact same prefix-based semantics the Logger
    methods emit (`:: header ::`, `## header2 ##`, `* item`, etc)
    but renders them beautifully with rich.  DEBUG/INFO/NOTICE and all layout
    helpers print to STDOUT, WARNING/ERROR/CRITICAL print to STDERR.  NOTICE is
    a real custom log level (25) so the file handler's levelname column shows it.

    This is a proper logging.Handler so log levels, filters and the file handler
    all continue to behave exactly as before.
    """

    def __init__(self, level=logging.NOTSET, *, colors=True):
        super().__init__(level=level)
        # No explicit file= so each Console resolves sys.stdout/sys.stderr lazily
        # at print time.  This keeps pytest's capture and any stream redirection
        # working (rich would otherwise pin the stream at construction time).
        self._stdout = Console(theme=UVICORE_LOG_THEME, stderr=False, no_color=not colors, markup=False, highlight=False, emoji=False)
        self._stderr = Console(theme=UVICORE_LOG_THEME, stderr=True, no_color=not colors, markup=False, highlight=False, emoji=False)

    def emit(self, record):
        try:
            console = self._stderr if record.levelno >= logging.WARNING else self._stdout
            renderable = self._render(record)
            # Rules must expand to the console width; everything else soft-wraps
            # (no hard wrapping) so long lines like SQL stay intact and let the
            # terminal wrap them, matching the old behavior.
            if isinstance(renderable, Rule):
                console.print(renderable)
            else:
                console.print(renderable, soft_wrap=True)
        except Exception:  # noqa: BLE001 - logging handlers must never raise
            self.handleError(record)

    def _render(self, record):
        """Turn a log record into a rich renderable."""
        message = self.format(record)
        level = record.levelname
        stripped = message.strip()

        # Blank line
        if stripped == '':
            return Text('')

        # Level based styling (everything that is not a plain INFO message)
        if level == 'DEBUG':
            return Text.assemble((DEBUG_GLYPH + ' ', 'log.debug.icon'), (message, 'log.debug'))
        if level == 'NOTICE':
            return Text.assemble((f' {NOTICE_GLYPH} NOTICE ', 'log.notice.label'), ' ', (message, 'log.notice'))
        if level == 'WARNING':
            return Text.assemble((WARNING_GLYPH + '  ', 'log.warning.icon'), (message, 'log.warning'))
        if level == 'ERROR':
            return Text.assemble((ERROR_GLYPH + '  ', 'log.error.icon'), (message, 'log.error'))
        if level == 'CRITICAL':
            return Text.assemble((' CRITICAL ', 'log.critical.label'), ' ', (message, 'log.critical'))

        # INFO level - parse the layout-helper prefixes
        return self._render_info(message, stripped)

    def _render_info(self, message, stripped):
        # separator() -> a full line of '='
        if len(stripped) >= 3 and set(stripped) == {'='}:
            return Rule(style='log.rule', characters='═')

        # line() -> a full line of '-'
        if len(stripped) >= 3 and set(stripped) == {'-'}:
            return Rule(style='log.rule', characters='─')

        # header()  :: X ::  -> full width rule with centered title
        if stripped.startswith(':: ') and stripped.endswith(' ::') and len(stripped) > 5:
            title = stripped[3:-3]
            return Rule(title=Text(f' {title} ', style='header.title'), characters='═', style='header.rule')

        # header2()  ## X ##  -> full width rule with centered title
        if stripped.startswith('## ') and stripped.endswith(' ##') and len(stripped) > 5:
            title = stripped[3:-3]
            return Rule(title=Text(f' {title} ', style='header2.title'), characters='─', style='header2.rule')

        # header3()  === X ===  -> inline styled text
        if stripped.startswith('=== ') and stripped.endswith(' ===') and len(stripped) > 7:
            title = stripped[4:-4]
            return Text.assemble(('=== ', 'header3.mark'), (title, 'header3.title'), (' ===', 'header3.mark'))

        # header4()  ---- X ----  -> inline styled text
        if stripped.startswith('---- ') and stripped.endswith(' ----') and len(stripped) > 9:
            title = stripped[5:-5]
            return Text.assemble(('---- ', 'header4.mark'), (title, 'header4.title'), (' ----', 'header4.mark'))

        # item()/item2()/item3()/item4() -> colored glyph + text (indent preserved)
        indent = message[:len(message) - len(message.lstrip())]
        for prefix, style in (('* ', 'item.mark'), ('- ', 'item2.mark'), ('+ ', 'item3.mark'), ('> ', 'item4.mark')):
            if stripped.startswith(prefix):
                body = stripped[len(prefix):]
                return Text.assemble(indent, (ITEM_GLYPHS[prefix] + ' ', style), (body, 'item.text'))

        # Plain old .info()
        return Text(message, style='log.info')


@uvicore.service('uvicore.logging.logger.Logger',
    aliases=['Logger', 'logger', 'Log', 'log'],
    singleton=True,
    kwargs={'config': uvicore.config('app.logger')},
)
class Logger(LoggerInterface):
    """Logger private class.

    Do not import from this location.
    Use the uvicore.log singleton global instead."""

    def __init__(self, config):
        # Default Config
        # Levels from logging._levelToName are
        # {50: 'CRITICAL', 40: 'ERROR', 30: 'WARNING', 20: 'INFO', 10: 'DEBUG', 0: 'NOTSET'}

        # Levels = DEBUG, INFO, WARNING, ERROR, CRITICAL
        default = {
            'console': {
                'enabled': True,
                'level': 'DEBUG',
                'colors': True,
                'format': '%(message)s',
                'filters': [],
                'exclude': [],
            },
            'file': {
                'enabled': False,
                'level': 'DEBUG',
                'file': '/tmp/example.log',
                'when': 'midnight',
                'interval': 1,
                'backup_count': 7,
                'format': '%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-22s | %(message)s',
                'filters': [],
                'exclude': [],
            }
        }

        # Merge default and user defined config
        config = {**default, **config}
        if 'console' in config.keys(): config['console'] = {**default['console'], **config['console']}
        if 'file' in config.keys(): config['file'] = {**default['file'], **config['file']}

        # New Logger
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.DEBUG)
        self._name = None

        # Explicit handler references (do not rely on handler list order)
        self._console_handler = None
        self._file_handler = None

        # New Console Handler
        # colors=True renders beautifully with rich (STDOUT/STDERR split).
        # colors=False falls back to a plain, ASCII, STDOUT-only StreamHandler
        # (no rich, raw prefixes) for anyone who explicitly wants dumb output.
        if config['console']['enabled']:
            if config['console']['colors']:
                handler = RichConsoleHandler(level=config['console']['level'], colors=True)
                handler.setFormatter(logging.Formatter(
                    fmt=config['console']['format'],
                    datefmt='%Y-%m-%d %H:%M:%S'
                ))
            else:
                handler = logging.StreamHandler(stream=sys.stdout)
                handler.setLevel(config['console']['level'])
                handler.setFormatter(logging.Formatter(
                    fmt=config['console']['format'],
                    datefmt='%Y-%m-%d %H:%M:%S'
                ))
            handler.addFilter(OutputFilter(config['console']['filters'], config['console']['exclude']))
            self._logger.addHandler(handler)
            self._console_handler = handler

        # New File Handler
        if config['file']['enabled']:
            #class logging.handlers.TimedRotatingFileHandler(filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False, atTime=None, errors=None)
            #handler = logging.FileHandler(filename=config['file']['file'], mode='a')
            handler = logging.handlers.TimedRotatingFileHandler(filename=config['file']['file'], when=config['file']['when'], interval=config['file']['interval'], backupCount=config['file']['backup_count'])
            handler.setLevel(config['file']['level'])
            handler.setFormatter(logging.Formatter(
                fmt=config['file']['format'],
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            #if config['file'].get('filter'): handler.addFilter(logging.Filter(name=config['file']['filter']))
            handler.addFilter(OutputFilter(config['file']['filters'], config['file']['exclude']))
            self._logger.addHandler(handler)
            self._file_handler = handler

        self.config = config

    def __call__(self, message):
        self.info(message)

    @property
    def console_handler(self) -> PythonLogger:
        return self._console_handler

    @property
    def file_handler(self) -> PythonLogger:
        return self._file_handler

    @property
    def logger(self):
        if not self._name: return self._logger
        return logging.getLogger(self._name)

    def name(self, name: str) -> LoggerInterface:
        self._name = name
        return self

    def reset(self):
        self._name = None

    def dump(self, *args):
        running_pytest = uvicore.app.is_pytest
        console_enabled = self.config['console']['enabled']
        console_level = logging.getLevelName(self.console_handler.level) if console_enabled else ''
        console_filters = self.config['console']['filters']
        console_excludes = self.config['console']['exclude']
        file_enabled = self.config['file']['enabled']
        file_level = logging.getLevelName(self.file_handler.level) if file_enabled else ''


        # Use dump() to prettyprint to console only if console is in DEBUG mode or we are running a pytest.
        # The dump() does not understand log filters and excludes, so we must use those manually to decide
        # if we should dump() the content or not.
        if (console_enabled and console_level == 'DEBUG') or running_pytest:
            show = False
            loggerName = self._name or 'root'

            # Check filters
            if not console_filters: show = True
            if not show:
                for filter in console_filters:
                    if loggerName[0:len(filter)] == filter:
                        show = True
                        break

            # Check excludes
            if show and console_excludes:
                for exclude in console_excludes:
                    if loggerName[0:len(exclude)] == exclude:
                        show = False
                        break

            # Loglevel, Filters and Excludes say we can dump this to the console
            if show: dump(*args)

        # Dump to file
        if (file_enabled and file_level == 'DEBUG'):
            # We must temporarily disable the console handler or this prints to the console as well
            # which means a double print because of the dump(*args) above.
            console_handler = self.console_handler
            saved_level = None
            if console_handler is not None:
                saved_level = console_handler.level
                console_handler.setLevel(logging.CRITICAL)

            # Log to file in DEBUG mode
            for arg in args:
                self.logger.debug(arg)

            # Re-enable the console handler by restoring its original level
            if console_handler is not None:
                console_handler.setLevel(saved_level)

        # Reset logger name
        self.reset()

    def info(self, message):
        self.logger.info(str(message))
        self.reset()

    def notice(self, message):
        self.logger.log(NOTICE, str(message))
        self.reset()

    def warning(self, message):
        self.logger.warning(str(message))
        self.reset()

    def debug(self, message):
        self.logger.debug(str(message))
        self.reset()

    def error(self, message):
        self.logger.error(str(message))
        self.reset()

    def critical(self, message):
        self.logger.critical(str(message))
        self.reset()

    def exception(self, message):
        self.logger.error(str(message))
        self.reset()

    def blank(self):
        self.logger.info('')
        self.reset()

    def nl(self) -> LoggerInterface:
        """nl() is a blank() that is chainable"""
        self.logger.info('')
        return self

    def separator(self):
        self.logger.info('=' * 80)
        self.reset()

    def line(self):
        self.logger.info('-' * 80)
        self.reset()

    def header(self, message):
        self.logger.info(":: " + str(message) + " ::")
        self.reset()

    def header2(self, message):
        self.logger.info("## " + str(message) + " ##")
        self.reset()

    def header3(self, message):
        self.logger.info("=== " + str(message) + " ===")
        self.reset()

    def header4(self, message):
        self.logger.info("---- " + str(message) + " ----")
        self.reset()

    def item(self, message, *, level: int = 1):
        spaces = ' ' * (level * 4)
        self.logger.info(spaces + "* " + str(message))
        self.reset()

    def item2(self, message, *, level: int = 1):
        spaces = ' ' * (level * 4)
        self.logger.info(spaces + "- " + str(message))
        self.reset()

    def item3(self, message, *, level: int = 1):
        spaces = ' ' * (level * 4)
        self.logger.info(spaces + "+ " + str(message))
        self.reset()

    def item4(self, message, *, level: int = 1):
        spaces = ' ' * (level * 4)
        self.logger.info(spaces + "> " + str(message))
        self.reset()



# IoC Class Instance
# Not to be imported by the public from here.
# Use the uvicore.log singleton global instead.

# Public API for import * and doc gens
#__all__ = ['_Logger', 'RichConsoleHandler']
