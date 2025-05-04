from __future__ import annotations
from typing import Any
from abc import ABC, abstractmethod
from logging import Logger as PythonLogger


class Logger(ABC):

    @property
    @abstractmethod
    def console_handler(self) -> PythonLogger:
        """Get the console logger"""

    @property
    @abstractmethod
    def file_handler(self) -> PythonLogger:
        """Get the file logger"""

    @property
    @abstractmethod
    def logger(self):
        """Get the logger"""

    @abstractmethod
    def name(self, name: str) -> Logger:
        """Set name of logger"""

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
    def nl(self) -> Logger:
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
