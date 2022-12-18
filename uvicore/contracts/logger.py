from __future__ import annotations
from abc import ABC, abstractmethod, abstractproperty
from typing import Dict, Any
from logging import Logger as PythonLogger

class Logger(ABC):

    @property
    @abstractmethod
    def console_handler(self) -> PythonLogger:
        """Get the console logger"""

    @abstractproperty
    @abstractmethod
    def file_handler(self) -> PythonLogger:
        """Get the file logger"""

    @abstractproperty
    @abstractmethod
    def logger(self):
        """Get the logger"""

    @abstractmethod
    def name(self, name: str):
        """Set name of logger"""

    @abstractmethod
    def reset(self):
        """Clear logger name"""

    @abstractmethod
    def dump(self, *args):
        """Dump message"""

    @abstractmethod
    def info(self, message) -> Logger:
        """Log an info message"""

    @abstractmethod
    def notice(self, message) -> Logger:
        """Log a notice message"""

    @abstractmethod
    def warning(self, message) -> Logger:
        """Log a warning message"""

    @abstractmethod
    def debug(self, message) -> Logger:
        """Log a debug message"""

    @abstractmethod
    def error(self, message) -> Logger:
        """Log an error message"""

    @abstractmethod
    def critical(self, message) -> Logger:
        """Log a critical message"""

    @abstractmethod
    def exception(self, message) -> Logger:
        """Log an exception message"""

    @abstractmethod
    def blank(self) -> Logger:
        """Log a blank line"""

    @abstractmethod
    def nl(self) -> Logger:
        """Log a blank line"""

    @abstractmethod
    def separator(self) -> Logger:
        """Log a = line separator"""

    @abstractmethod
    def line(self) -> Logger:
        """Log a - line separator"""

    @abstractmethod
    def header(self, message) -> Logger:
        """Header :: style"""

    @abstractmethod
    def header2(self, message) -> Logger:
        """Header ## style"""

    @abstractmethod
    def header3(self, message) -> Logger:
        """Header === style"""

    @abstractmethod
    def header4(self, message) -> Logger:
        """Header ---- style"""

    @abstractmethod
    def item(self, message) -> Logger:
        """Item * style"""

    @abstractmethod
    def item2(self, message) -> Logger:
        """Item - style"""

    @abstractmethod
    def item3(self, message) -> Logger:
        """Item + style"""

    @abstractmethod
    def item4(self, message) -> Logger:
        """Item > style"""
