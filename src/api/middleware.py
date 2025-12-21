"""Flask middleware for request/response processing.

This module provides middleware for logging, request tracking, and error handling.
Follows Single Responsibility Principle.
"""

import time
import uuid
from flask import Flask, request, g
from typing import Callable

from ..core.interfaces import LoggerProtocol


class RequestLoggingMiddleware:
    """Middleware for request logging and timing.
    
    Handles request ID generation and timing for all requests.
    """
    
    def __init__(self, app: Flask, logger: LoggerProtocol):
        """Initialize middleware.
        
        Args:
            app: Flask application instance.
            logger: Logger for dependency injection.
        """
        self.app = app
        self.logger = logger
        self._setup_middleware()
    
    def _setup_middleware(self) -> None:
        """Set up before and after request handlers."""
        self.app.before_request(self._before_request)
        self.app.after_request(self._after_request)
    
    def _before_request(self) -> None:
        """Process before each request."""
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        g.start_time = time.time()
        
        self.logger.info(
            f"Incoming request {request.method} {request.path}",
            request_id=g.request_id,
            duration=0
        )
    
    def _after_request(self, response) -> object:
        """Process after each request.
        
        Args:
            response: Flask response object.
            
        Returns:
            Modified response object.
        """
        duration_ms = int((time.time() - getattr(g, "start_time", time.time())) * 1000)
        request_id = getattr(g, "request_id", "-")
        
        self.logger.info(
            f"Response {request.method} {request.path} status={response.status_code} duration={duration_ms}ms",
            request_id=request_id,
            duration=duration_ms
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


class ErrorHandlingMiddleware:
    """Middleware for global error handling."""
    
    def __init__(self, app: Flask, logger: LoggerProtocol):
        """Initialize error handling middleware.
        
        Args:
            app: Flask application instance.
            logger: Logger for dependency injection.
        """
        self.app = app
        self.logger = logger
        self._setup_error_handlers()
    
    def _setup_error_handlers(self) -> None:
        """Set up global error handlers."""
        self.app.register_error_handler(404, self._handle_404)
        self.app.register_error_handler(500, self._handle_500)
        self.app.register_error_handler(Exception, self._handle_exception)
    
    def _handle_404(self, error):
        """Handle 404 errors."""
        self.logger.warning(f"404 Not Found: {request.path}")
        return {"error": "Not found"}, 404
    
    def _handle_500(self, error):
        """Handle 500 errors."""
        self.logger.exception("Internal server error occurred")
        return {"error": "Internal server error"}, 500
    
    def _handle_exception(self, error):
        """Handle uncaught exceptions."""
        self.logger.exception(f"Unhandled exception: {str(error)}")
        return {"error": "Internal server error"}, 500


def setup_middleware(app: Flask, logger: LoggerProtocol) -> None:
    """Set up all middleware for the application.
    
    Args:
        app: Flask application instance.
        logger: Logger instance for dependency injection.
    """
    RequestLoggingMiddleware(app, logger)
    ErrorHandlingMiddleware(app, logger)