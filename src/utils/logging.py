"""Logging utilities.

This module provides logging configuration and a logger adapter that implements
the LoggerProtocol interface. Follows Single Responsibility Principle.
"""

import logging
import os
from typing import Optional
from logging.handlers import RotatingFileHandler

from ..core.interfaces import LoggerProtocol
from ..config.settings import LoggingConfig


class RequestContextFilter(logging.Filter):
    """Filter to provide default context for log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add default context if not present."""
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        if not hasattr(record, "duration"):
            record.duration = 0
        return True


class StructuredLogger(LoggerProtocol):
    """Structured logger implementation with request context support.
    
    Implements LoggerProtocol interface for dependency injection.
    """
    
    def __init__(self, name: str, config: LoggingConfig):
        """Initialize structured logger.
        
        Args:
            name: Logger name.
            config: Logging configuration.
        """
        self.config = config
        self.logger = self._setup_logger(name)
    
    def _setup_logger(self, name: str) -> logging.Logger:
        """Set up logger with handlers and formatters."""
        logger = logging.getLogger(name)
        
        if logger.handlers:
            # Already configured
            return logger
        
        # Set logging level
        level = getattr(logging, self.config.level.upper(), logging.INFO)
        logger.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            fmt=(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s "
                "[req_id=%(request_id)s duration=%(duration)sms]"
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        try:
            log_file = os.path.join(os.path.dirname(__file__), "..", "..", self.config.log_file)
            file_handler = RotatingFileHandler(
                log_file, 
                maxBytes=1_000_000, 
                backupCount=3
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            # If file handler fails, proceed with console only
            pass
        
        # Add context filter
        logger.addFilter(RequestContextFilter())
        
        return logger
    
    def _get_extra(self, **kwargs) -> dict:
        """Get extra context for logging."""
        extra = kwargs.copy()
        
        # Try to get Flask request context
        try:
            from flask import g
            extra.setdefault("request_id", getattr(g, "request_id", "-"))
            if hasattr(g, "start_time"):
                import time
                duration = int((time.time() - g.start_time) * 1000)
                extra.setdefault("duration", duration)
        except (RuntimeError, ImportError):
            # Outside Flask context or Flask not available
            extra.setdefault("request_id", "-")
            extra.setdefault("duration", 0)
        
        return extra
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        extra = self._get_extra(**kwargs)
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        extra = self._get_extra(**kwargs)
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        extra = self._get_extra(**kwargs)
        self.logger.error(message, extra=extra)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        extra = self._get_extra(**kwargs)
        self.logger.debug(message, extra=extra)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        extra = self._get_extra(**kwargs)
        self.logger.exception(message, extra=extra)


def create_logger(name: str, config: LoggingConfig) -> StructuredLogger:
    """Factory function to create a structured logger.
    
    Args:
        name: Logger name.
        config: Logging configuration.
        
    Returns:
        StructuredLogger: Configured logger instance.
    """
    return StructuredLogger(name, config)