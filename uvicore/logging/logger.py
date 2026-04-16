from __future__ import annotations

import re
import sys
import uvicore
import logging
import logging.config
from logging import Formatter
from uvicore.typing import List
from colored import attr, bg, fg
from logging import Logger as PythonLogger
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
            print(exclude)
            if record.name[0:len(exclude)] == exclude: return False
        return True


class ColoredFormatter(Formatter):

    def __init__(self, patern):
        Formatter.__init__(self, patern)

    def format(self, record):
        # Remember this is console output only, not file or other handlers
        # See color chart https://pypi.org/project/colored/
        level = record.levelname
        message = logging.Formatter.format(self, record)
        prefix = str(message.strip()[0:2]).strip()

        # Format all INFO level messages
        if level == 'INFO':

            # Format header
            if prefix == '::':
                message = re.sub("^:: ", "", message)
                message = re.sub(" ::$", "", message)
                message = ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), ':: ', attr(0)) \
                    + ('{0}{1}{2}{3}').format(fg('green'), attr('bold'), message, attr(0)) \
                    + ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), ' ::', attr(0))

            # Format header2
            if prefix == '##':
                message = re.sub("^## ", "", message)
                message = re.sub(" ##$", "", message)
                message = ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), '## ', attr(0)) \
                    + ('{0}{1}{2}{3}').format(fg('green'), attr('bold'), message, attr(0)) \
                    + ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), ' ##', attr(0))

            # Format header3
            if prefix == '==':
                message = re.sub("^=== ", "", message)
                message = re.sub(" ===$", "", message)
                message = ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), '=== ', attr(0)) \
                    + ('{0}{1}{2}').format(fg('green'), message, attr(0)) \
                    + ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), ' ===', attr(0))

            # Format header4
            if prefix == '--':
                message = re.sub("^---- ", "", message)
                message = re.sub(" ----$", "", message)
                message = ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), '---- ', attr(0)) \
                    + ('{0}{1}{2}').format(fg('dark_green'), message, attr(0)) \
                    + ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), ' ----', attr(0))

            # Format item *
            elif prefix == '*':
                split = message.split('*')
                pre = split[0] + '*'
                post = '*'.join(split[1:])
                message = ('{0}{1}{2}').format(fg('green'), pre, attr(0)) \
                    + ('{0}{1}{2}{3}').format(fg('white'), attr('bold'), post, attr(0))

            # Format item2 -
            elif prefix == '-':
                split = message.split('-')
                pre = split[0] + '-'
                post = '-'.join(split[1:])
                message = ('{0}{1}{2}').format(fg('red'), pre, attr(0)) \
                    + ('{0}{1}{2}{3}').format(fg('white'), attr('bold'), post, attr(0))

            # Format item3 +
            elif prefix == '+':
                split = message.split('+')
                pre = split[0] + '+'
                post = '+'.join(split[1:])
                message = ('{0}{1}{2}').format(fg('cyan'), pre, attr(0)) \
                    + ('{0}{1}{2}{3}').format(fg('white'), attr('bold'), post, attr(0))

            # Format item4 >
            elif prefix == '>':
                split = message.split('>')
                pre = split[0] + '>'
                post = '>'.join(split[1:])
                message = ('{0}{1}{2}').format(fg('magenta'), pre, attr(0)) \
                    + ('{0}{1}{2}{3}').format(fg('white'), attr('bold'), post, attr(0))

            # Format notice
            elif (level == 'INFO' and re.match("^NOTICE: ", message)):
                message = re.sub("^NOTICE: ", "", message)
                message = ('{0}{1}{2}{3}').format(fg('yellow'), attr('bold'), 'NOTICE: ', attr(0)) \
                    + ('{0}{1}{2}{3}').format(fg('white'), attr('bold'), message, attr(0))

            # Format separator
            elif (level == 'INFO' and re.match("^====", message)):
                message = ('{0}{1}{2}{3}').format(fg('orange_4a'), attr('bold'), message, attr(0))

            # Format line
            elif (level == 'INFO' and re.match("^----", message)):
                message = ('{0}{1}{2}{3}').format(fg('orange_4a'), attr('bold'), message, attr(0))

            # No special formatting, plain old .info()
            else:
                message = message

        elif (level == 'DEBUG'):
            message = ('{0}{1}{2}').format(fg(241), message, attr(0))

        elif (level == 'WARNING'):
            message = ('{0}{1}{2}').format(fg('orange_red_1'), message, attr(0))
        elif (level == 'ERROR'):
            message = ('{0}{1}{2}').format(fg('red'), message, attr(0))
        elif (level == 'CRITICAL'):
            message = ('{0}{1}{2}{3}').format(fg('black'), bg('red'), message, attr(0))

        return message


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

        # New Console Handler
        if config['console']['enabled']:
            handler = logging.StreamHandler(stream=sys.stdout)
            handler.setLevel(config['console']['level'])
            if config['console']['colors']:
                handler.setFormatter(ColoredFormatter(config['console']['format']))
            else:
                handler.setFormatter(logging.Formatter(
                    fmt=config['console']['format'],
                    datefmt='%Y-%m-%d %H:%M:%S'
                ))
            handler.addFilter(OutputFilter(config['console']['filters'], config['console']['exclude']))
            self._logger.addHandler(handler)

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

        self.config = config

    def __call__(self, message):
        self.info(message)

    @property
    def console_handler(self) -> PythonLogger:
        try:
            return self._logger.handlers[0]
        except IndexError:
            return None

    @property
    def file_handler(self) -> PythonLogger:
        try:
            return self._logger.handlers[1]
        except IndexError:
            return None

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
        console_level = logging.getLevelName(uvicore.log.console_handler.level) if console_enabled else ''
        console_filters = self.config['console']['filters']
        console_excludes = self.config['console']['exclude']
        file_enabled = self.config['file']['enabled']
        file_level = logging.getLevelName(uvicore.log.file_handler.level) if file_enabled else ''


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
            # We must temporarily disable the console logger or this prints to the console as well
            # Which means a double print because of the dump(*args) abvove
            # Must get handlers from the root logger.  If we are using a custom logger name like 'my-section' then it has no handlers
            # so self.logger.handlers does not work.  We want the 'root' logger handlers
            root_handlers = logging.getLogger().handlers
            for handler in root_handlers:
                if 'logging.StreamHandler' in str(type(handler)):
                    handler.setLevel('CRITICAL')

            # Log to file in in DEBUG mode
            for arg in args:
                self.logger.debug(arg)

            # Re-enable console logger by restoring the original level
            for handler in root_handlers:
                if 'logging.StreamHandler' in str(type(handler)):
                    handler.setLevel(console_level)

        # Reset logger name
        self.reset()

    def info(self, message):
        self.logger.info(str(message))
        self.reset()

    def notice(self, message):
        self.logger.info("NOTICE: " + str(message))
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
#__all__ = ['_Logger', 'ColoredFormatter']
