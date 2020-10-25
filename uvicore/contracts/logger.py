from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any
from logging import Logger as PythonLogger

class Logger(ABC):

    @property
    @abstractmethod
    def console_handler(self) -> PythonLogger:
        """Get the console logger"""
        pass

    @property
    @abstractmethod
    def file_handler(self) -> PythonLogger:
        """Get the file logger"""
        pass

    @abstractmethod
    def info(self, message) -> Logger:
        """Log an info message"""
        pass

    @abstractmethod
    def notice(self, message) -> Logger:
        """Log a notice message"""
        pass

    @abstractmethod
    def warning(self, message) -> Logger:
        """Log a warning message"""
        pass

    @abstractmethod
    def debug(self, message) -> Logger:
        """Log a debug message"""
        pass

    @abstractmethod
    def error(self, message) -> Logger:
        """Log an error message"""
        pass

    @abstractmethod
    def critical(self, message) -> Logger:
        """Log a critical message"""
        pass

    @abstractmethod
    def exception(self, message) -> Logger:
        """Log an exception message"""
        pass

    @abstractmethod
    def blank(self) -> Logger:
        """Log a blank line"""
        pass

    @abstractmethod
    def nl(self) -> Logger:
        """Log a blank line"""
        pass

    @abstractmethod
    def separator(self) -> Logger:
        """Log a = line separator"""
        pass

    @abstractmethod
    def line(self) -> Logger:
        """Log a - line separator"""
        pass

    @abstractmethod
    def header(self, message) -> Logger:
        """Header :: style"""
        pass

    @abstractmethod
    def header2(self, message) -> Logger:
        """Header ## style"""
        pass

    @abstractmethod
    def header3(self, message) -> Logger:
        """Header === style"""
        pass

    @abstractmethod
    def header4(self, message) -> Logger:
        """Header ---- style"""
        pass

    @abstractmethod
    def item(self, message) -> Logger:
        """Item * style"""
        pass

    @abstractmethod
    def item2(self, message) -> Logger:
        """Item - style"""
        pass

    @abstractmethod
    def item3(self, message) -> Logger:
        """Item + style"""
        pass

    @abstractmethod
    def item4(self, message) -> Logger:
        """Item > style"""
        pass
