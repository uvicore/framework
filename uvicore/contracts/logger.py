from __future__ import annotations
from abc import ABC, abstractmethod
from logging import Logger as PythonLogger
from logging import Handler as PythonHandler


class LogWriter(ABC):
    """Anything that can emit log messages.

    Shared by the uvicore.log singleton (the default channel) and by every named
    log channel."""

    @property
    @abstractmethod
    def console_handler(self) -> PythonHandler | None:
        """Get the console log handler, or None if console logging is disabled"""

    @property
    @abstractmethod
    def file_handler(self) -> PythonHandler | None:
        """Get the file log handler, or None if file logging is disabled"""

    @property
    @abstractmethod
    def logger(self) -> PythonLogger:
        """Get the underlying python logger"""

    @abstractmethod
    def reset(self):
        """Clear logger name"""

    @abstractmethod
    def dump(self, *args):
        """Dump message"""

    @abstractmethod
    def info(self, message):
        """Log an info message"""

    @abstractmethod
    def notice(self, message):
        """Log a notice message"""

    @abstractmethod
    def warning(self, message):
        """Log a warning message"""

    @abstractmethod
    def debug(self, message):
        """Log a debug message"""

    @abstractmethod
    def error(self, message):
        """Log an error message"""

    @abstractmethod
    def critical(self, message):
        """Log a critical message"""

    @abstractmethod
    def exception(self, message):
        """Log an exception message"""

    @abstractmethod
    def blank(self):
        """Log a blank line"""

    @abstractmethod
    def nl(self) -> LogWriter:
        """Log a blank line"""

    @abstractmethod
    def separator(self):
        """Log a = line separator"""

    @abstractmethod
    def line(self):
        """Log a - line separator"""

    @abstractmethod
    def header(self, message):
        """Header :: style"""

    @abstractmethod
    def header2(self, message):
        """Header ## style"""

    @abstractmethod
    def header3(self, message):
        """Header === style"""

    @abstractmethod
    def header4(self, message):
        """Header ---- style"""

    @abstractmethod
    def item(self, message, *, level: int = 1):
        """Item * style"""

    @abstractmethod
    def item2(self, message, *, level: int = 1):
        """Item - style"""

    @abstractmethod
    def item3(self, message, *, level: int = 1):
        """Item + style"""

    @abstractmethod
    def item4(self, message, *, level: int = 1):
        """Item > style"""


class LogChannel(LogWriter):
    """One named log channel with its own file and its own python logger.

    Obtained from uvicore.log.channel('Processor').  Immutable and safe to hold
    onto across awaits and across threads."""

    @property
    @abstractmethod
    def channel(self) -> str:
        """The name of this channel"""


class Logger(LogWriter):
    """The uvicore.log singleton, which is also the default log channel"""

    @abstractmethod
    def name(self, name: str) -> Logger:
        """Set the one-shot logger name used for filters and excludes (chainable).

        This is a filtering scope, not a destination - use channel() for a
        separate log file.  The scope is task local and cleared after one use."""

    @property
    @abstractmethod
    def channels(self) -> dict[str, LogChannel]:
        """All instantiated log channels"""

    @abstractmethod
    def channel(self, name: str) -> LogChannel:
        """Get a named log channel, lazily created and cached"""
