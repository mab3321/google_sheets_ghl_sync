"""Application configuration settings.

This module handles all configuration management following the Single Responsibility Principle.
It centralizes environment variable loading and validation.
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class GHLConfig:
    """GoHighLevel API configuration."""
    
    location_id: str
    schema_key: str
    api_key: str
    base_url: str = "https://services.leadconnectorhq.com"


@dataclass(frozen=True)
class FlaskConfig:
    """Flask application configuration."""
    
    host: str
    port: int
    debug: bool


@dataclass(frozen=True)
class LoggingConfig:
    """Logging configuration."""
    
    level: str
    log_file: str


@dataclass(frozen=True)
class AppConfig:
    """Main application configuration container."""
    
    ghl: GHLConfig
    flask: FlaskConfig
    logging: LoggingConfig


class ConfigurationError(Exception):
    """Raised when configuration validation fails."""
    pass


class ConfigLoader:
    """Configuration loader and validator.
    
    Follows Single Responsibility Principle by handling only configuration concerns.
    """
    
    # Fields that will be synced with GHL
    FIELDS_OF_INTEREST = [
        "stock_number",
        "make",
        "model",
        "trim",
        "year",
        "vehicle_type",
        "drive",
        "transmission",
        "cylinders",
        "fuel_type",
        "colour",
        "vin",
    ]
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration loader.
        
        Args:
            env_file: Path to .env file. If None, uses default .env discovery.
        """
        self._load_env_file(env_file)
    
    def _load_env_file(self, env_file: Optional[str]) -> None:
        """Load environment variables from file."""
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
    
    def _env_bool(self, name: str, default: bool = False) -> bool:
        """Parse boolean environment variable."""
        val = os.getenv(name)
        if val is None:
            return default
        return val.strip().lower() in {"1", "true", "yes", "on"}
    
    def _get_required_env(self, name: str) -> str:
        """Get required environment variable or raise error."""
        value = os.getenv(name)
        if not value:
            raise ConfigurationError(f"Required environment variable '{name}' is not set")
        return value
    
    def load(self) -> AppConfig:
        """Load and validate all configuration.
        
        Returns:
            AppConfig: Validated application configuration.
            
        Raises:
            ConfigurationError: If required configuration is missing or invalid.
        """
        # Load GHL configuration
        ghl_config = GHLConfig(
            location_id=self._get_required_env("GHL_LOCATION_ID"),
            schema_key=os.getenv("GHL_SCHEMA_KEY", "custom_objects.vehicles"),
            api_key=self._get_required_env("GHL_API_KEY"),
        )
        
        # Load Flask configuration
        flask_config = FlaskConfig(
            host=os.getenv("FLASK_HOST", "0.0.0.0"),
            port=int(os.getenv("FLASK_PORT", "5000")),
            debug=self._env_bool("FLASK_DEBUG", False),
        )
        
        # Load logging configuration
        logging_config = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "app.log"),
        )
        
        return AppConfig(
            ghl=ghl_config,
            flask=flask_config,
            logging=logging_config,
        )


# Global configuration instance
_config_loader = ConfigLoader()
config = _config_loader.load()