"""Main application factory following SOLID principles.

This module provides the Flask application factory with dependency injection.
Follows Single Responsibility and Dependency Inversion principles.
"""

from flask import Flask
from typing import Optional

from .config.settings import AppConfig, config
from .core.interfaces import RecordService, DataProcessor, LoggerProtocol
from .services.ghl_service import GHLRecordService
from .utils.logging import create_logger
from .utils.validators import VehicleDataProcessor
from .api.routes import create_routes
from .api.middleware import setup_middleware


class DependencyContainer:
    """Simple dependency injection container.
    
    Manages creation and lifecycle of application dependencies.
    Follows Dependency Inversion Principle.
    """
    
    def __init__(self, app_config: AppConfig):
        """Initialize container with configuration.
        
        Args:
            app_config: Application configuration.
        """
        self.config = app_config
        self._logger: Optional[LoggerProtocol] = None
        self._record_service: Optional[RecordService] = None
        self._data_processor: Optional[DataProcessor] = None
    
    @property
    def logger(self) -> LoggerProtocol:
        """Get logger instance (singleton)."""
        if self._logger is None:
            self._logger = create_logger("ghl_integration", self.config.logging)
        return self._logger
    
    @property
    def record_service(self) -> RecordService:
        """Get record service instance (singleton)."""
        if self._record_service is None:
            self._record_service = GHLRecordService(self.config.ghl, self.logger)
        return self._record_service
    
    @property
    def data_processor(self) -> DataProcessor:
        """Get data processor instance (singleton)."""
        if self._data_processor is None:
            self._data_processor = VehicleDataProcessor()
        return self._data_processor


def create_app(app_config: AppConfig = None) -> Flask:
    """Application factory function.
    
    Args:
        app_config: Optional configuration override for testing.
        
    Returns:
        Configured Flask application.
    """
    # Use provided config or load from environment
    app_config = app_config or config
    
    # Create Flask app
    app = Flask(__name__)
    app.config.update({
        "DEBUG": app_config.flask.debug,
        "TESTING": False,
    })
    
    # Initialize dependency container
    container = DependencyContainer(app_config)
    
    # Store container in app for access in other parts
    app.container = container
    
    # Set up middleware
    setup_middleware(app, container.logger)
    
    # Register routes
    routes_bp = create_routes(
        container.record_service,
        container.data_processor,
        container.logger
    )
    app.register_blueprint(routes_bp)
    
    # Log startup
    container.logger.info(
        f"Application created with debug={app_config.flask.debug}",
        request_id="startup",
        duration=0
    )
    
    return app


def run_app(app: Flask, app_config: AppConfig = None) -> None:
    """Run the Flask application.
    
    Args:
        app: Flask application instance.
        app_config: Optional configuration override.
    """
    app_config = app_config or config
    
    app.container.logger.info(
        f"Starting Flask app on {app_config.flask.host}:{app_config.flask.port} "
        f"debug={app_config.flask.debug}",
        request_id="startup",
        duration=0
    )
    
    app.run(
        host=app_config.flask.host,
        port=app_config.flask.port,
        debug=app_config.flask.debug
    )