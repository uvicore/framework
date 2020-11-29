from __future__ import annotations

import logging
import logging.config
import re
import sys
from logging import Formatter
from logging import Logger as PythonLogger

from colored import attr, bg, fg

import uvicore
from uvicore.contracts import Logger as LoggerInterface
from uvicore.support.dumper import dump

# # Sunfinity standardized log configuration
# config = {
#     'version': 1,
#     'formatters': {
#         'console': {
#             'format': '%(message)s',
#             'datefmt': '%Y-%m-%d %H:%M:%S',
#         },
#         'file': {
#             #format': ''%(asctime)s.%(msecs)03d | %(process)-5d | %(levelname)-7s | %(module)s:%(lineno)-10d | %(message)s'',
#             #format': ''%(asctime)s.%(msecs)03d | %(levelname)-7s | %(message)s'',
#             'format': '%(asctime)s.%(msecs)03d | %(levelname)-7s | %(message)s',
#             'datefmt': '%Y-%m-%d %H:%M:%S',
#         },
#     },
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#             'level': 'INFO',
#             'formatter': 'console',
#             'stream': 'ext://sys.stdout',
#         },
#         'file': {
#             'class': 'logging.handlers.RotatingFileHandler',
#             'level': 'DEBUG',
#             'formatter': 'file',
#             'filename': file,
#             'maxBytes': 1024,
#             'backupCount': 3,
#         },
#     },
#     'root': {
#         'level': 'DEBUG',
#         'handlers': ['console', 'file'],
#     }
# }


class _OutputFilter(logging.Filter):
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



class _ExcludeFilter(logging.Filter):
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


class _ColoredFormatter(Formatter):

    def __init__(self, patern):
        Formatter.__init__(self, patern)

    def format(self, record):
        # Remember this is console output only, not file or other handlers
        # See color chart https://pypi.org/project/colored/
        level = record.levelname
        message = logging.Formatter.format(self, record)

        # Format header
        if (level == 'INFO' and re.match("^:: ", message)):
            message = re.sub("^:: ", "", message)
            message = re.sub(" ::$", "", message)
            message = ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), ':: ', attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('green'), attr('bold'), message, attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), ' ::', attr(0))

        # Format header2
        if (level == 'INFO' and re.match("^## ", message)):
            message = re.sub("^## ", "", message)
            message = re.sub(" ##$", "", message)
            message = ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), '## ', attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('green'), attr('bold'), message, attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), ' ##', attr(0))

        # Format header3
        if (level == 'INFO' and re.match("^=== ", message)):
            message = re.sub("^=== ", "", message)
            message = re.sub(" ===$", "", message)
            message = ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), '=== ', attr(0)) \
                + ('{0}{1}{2}').format(fg('green'), message, attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), ' ===', attr(0))

        # Format header4
        if (level == 'INFO' and re.match("^---- ", message)):
            message = re.sub("^---- ", "", message)
            message = re.sub(" ----$", "", message)
            message = ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), '---- ', attr(0)) \
                + ('{0}{1}{2}').format(fg('dark_green'), message, attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('dark_orange'), attr('bold'), ' ----', attr(0))

        # Format bullet * item
        elif (level == 'INFO' and re.match("^\* ", message)):
            message = re.sub("^\* ", "", message)
            message = ('{0}{1}{2}').format(fg('green'), '   * ', attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('white'), attr('bold'), message, attr(0))

        # Format bullet2 - item
        elif (level == 'INFO' and re.match("^- ", message)):
            message = re.sub("^- ", "", message)
            message = ('{0}{1}{2}').format(fg('cyan'), '   - ', attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('white'), attr('bold'), message, attr(0))

        # Format bullet3 + item
        elif (level == 'INFO' and re.match("^\+ ", message)):
            message = re.sub("^\+ ", "", message)
            message = ('{0}{1}{2}').format(fg('red'), '   + ', attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('white'), attr('bold'), message, attr(0))

        # Format bullet4 > item
        elif (level == 'INFO' and re.match("^> ", message)):
            message = re.sub("^> ", "", message)
            message = ('{0}{1}{2}').format(fg('magenta'), '   > ', attr(0)) \
                + ('{0}{1}{2}{3}').format(fg('white'), attr('bold'), message, attr(0))

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

        elif (level == 'DEBUG'):
            message = ('{0}{1}{2}').format(fg(241), message, attr(0))
        elif (level == 'INFO'):
            message = message
        elif (level == 'WARNING'):
            message = ('{0}{1}{2}').format(fg('orange_red_1'), message, attr(0))
        elif (level == 'ERROR'):
            message = ('{0}{1}{2}').format(fg('red'), message, attr(0))
        elif (level == 'CRITICAL'):
            message = ('{0}{1}{2}{3}').format(fg('black'), bg('red'), message, attr(0))

        return message


@uvicore.service('uvicore.logging.logger._Logger',
    aliases=['Logger', 'logger', 'Log', 'log'],
    singleton=True,
    kwargs={'config': uvicore.config('app.logger')},
)
class _Logger(LoggerInterface):
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
                handler.setFormatter(_ColoredFormatter(config['console']['format']))
            else:
                handler.setFormatter(logging.Formatter(
                    fmt=config['console']['format'],
                    datefmt='%Y-%m-%d %H:%M:%S'
                ))
            handler.addFilter(_OutputFilter(config['console']['filters'], config['console']['exclude']))
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
            handler.addFilter(_OutputFilter(config['file']['filters'], config['file']['exclude']))
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

    def name(self, name: str):
        self._name = name
        return self

    def reset(self):
        self._name = None

    def dump(self, *args):
        self._dump_handler(*args, handler='file', filters=self.config['file']['filters'], excludes=self.config['file']['exclude'])
        self._dump_handler(*args, handler='console', filters=self.config['console']['filters'], excludes=self.config['console']['exclude'])
        self.reset()

    def _dump_handler(self, *args, handler: str, filters: List, excludes: List):
        if not self._name: self.name == 'root'
        show = False

        # Check filters
        if not filters: show = True
        if not show and self._name:
            for filter in filters:
                if self._name[0:len(filter)] == filter:
                    show = True
                    break

        # Check excludes
        if show and excludes:
            for exclude in excludes:
                if self._name[0:len(exclude)] == exclude:
                    show = False
                    break

        if show:
            if handler == 'console':
                # Pretty Printer to Console
                dump(*args)
            else:
                # Print as text to file handler
                for arg in args:
                    self.logger.debug(arg)

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
        self.logger.exception(str(message))
        self.reset()

    def blank(self) -> LoggerInterface:
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

    def item(self, message):
        self.logger.info("* " + str(message))
        self.reset()

    def item2(self, message):
        self.logger.info("- " + str(message))
        self.reset()

    def item3(self, message):
        self.logger.info("+ " + str(message))
        self.reset()

    def item4(self, message):
        self.logger.info("> " + str(message))
        self.reset()



# IoC Class Instance
# Not to be imported by the public from here.
# Use the uvicore.log singleton global instead.

# Public API for import * and doc gens
#__all__ = ['_Logger', 'ColoredFormatter']
