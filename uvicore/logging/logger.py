from __future__ import annotations

import logging
import logging.config
import re
import sys
from logging import Formatter

from colored import attr, bg, fg

import uvicore
from uvicore.contracts import Logger as LoggerInterface

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



class _Logger(LoggerInterface):
    """Logger private class.

    Do not import from this location.
    Use the uvicore.log singleton global instead."""

    def __init__(self, config):
        # Default Config
        # Levels = NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
        default = {
            'console': {
                'enabled': True,
                'level': 'DEBUG',
                'colors': True,
                'format': '%(message)s'
            },
            'file': {
                'enabled': False,
                'level': 'DEBUG',
                'file': '/tmp/example.log',
                'format': '%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s | %(message)s'
            }
        }

        # Merge default and user defined config
        config = {**default, **config}
        if 'console' in config.keys(): config['console'] = {**default['console'], **config['console']}
        if 'file' in config.keys(): config['file'] = {**default['file'], **config['file']}
        self.config = config

        # New Logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # New Console Handler
        if config['console']['enabled']:
            ch = logging.StreamHandler(stream=sys.stdout)
            ch.setLevel(config['console']['level'])
            if config['console']['colors']:
                ch.setFormatter(ColoredFormatter(config['console']['format']))
            else:
                ch.setFormatter(logging.Formatter(
                    fmt=config['console']['format'],
                    datefmt='%Y-%m-%d %H:%M:%S'
                ))
            logger.addHandler(ch)

        # New File Handler
        if config['file']['enabled']:
            fh = logging.FileHandler(filename=config['file']['file'], mode='a')
            fh.setLevel(config['file']['level'])
            fh.setFormatter(logging.Formatter(
                fmt=config['file']['format'],
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            logger.addHandler(fh)

    def __call__(self, message):
        self.info(message)

    def info(self, message) -> LoggerInterface:
        logging.info(message)
        return self

    def notice(self, message) -> LoggerInterface:
        logging.info("NOTICE: " + message)
        return self

    def warning(self, message) -> LoggerInterface:
        logging.warning(message)
        return self

    def debug(self, message) -> LoggerInterface:
        logging.debug(message)
        return self

    def error(self, message) -> LoggerInterface:
        logging.error(message)
        return self

    def critical(self, message) -> LoggerInterface:
        logging.critical(message)
        return self

    def exception(self, message) -> LoggerInterface:
        logging.exception(message)
        return self

    def blank(self) -> LoggerInterface:
        logging.info('')
        return self

    def separator(self) -> LoggerInterface:
        logging.info('=' * 80)
        return self

    def line(self) -> LoggerInterface:
        logging.info('-' * 80)
        return self

    def header(self, message) -> LoggerInterface:
        logging.info(":: " + message + " ::")
        return self

    def header2(self, message) -> LoggerInterface:
        logging.info("## " + message + " ##")
        return self

    def header3(self, message) -> LoggerInterface:
        logging.info("=== " + message + " ===")
        return self

    def header4(self, message) -> LoggerInterface:
        logging.info("---- " + message + " ----")
        return self

    def item(self, message) -> LoggerInterface:
        logging.info("* " + message)
        return self

    def item2(self, message) -> LoggerInterface:
        logging.info("- " + message)
        return self

    def item3(self, message) -> LoggerInterface:
        logging.info("+ " + message)
        return self

    def item4(self, message) -> LoggerInterface:
        logging.info("> " + message)
        return self


class ColoredFormatter(Formatter):

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
            message = ('{0}{1}{2}{3}').format(fg('white'), bg('red'), message, attr(0))

        return message


# IoC Class Instance
# Not to be imported by the public from here.
# Use the uvicore.log singleton global instead.

# Public API for import * and doc gens
__all__ = ['_Logger', 'ColoredFormatter']
