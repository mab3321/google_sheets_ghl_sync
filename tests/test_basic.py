"""Test configuration and basic functionality."""

import pytest
import os
from unittest.mock import patch

from src.config.settings import ConfigLoader, ConfigurationError, AppConfig
from src.utils.validators import VehicleDataProcessor, validate_request_payload, ValidationError


class TestConfiguration:
    """Test configuration loading and validation."""
    
    def test_config_loader_requires_env_vars(self):
        """Test that required environment variables are validated."""
        with patch.dict(os.environ, {}, clear=True):
            loader = ConfigLoader()
            with pytest.raises(ConfigurationError):
                loader.load()
    
    def test_config_loader_with_valid_env(self):
        """Test configuration loading with valid environment."""
        env_vars = {
            "GHL_LOCATION_ID": "test_location",
            "GHL_API_KEY": "test_key",
            "GHL_SCHEMA_KEY": "test_schema",
            "FLASK_HOST": "127.0.0.1",
            "FLASK_PORT": "8000",
            "FLASK_DEBUG": "false",
            "LOG_LEVEL": "DEBUG"
        }
        
        with patch.dict(os.environ, env_vars):
            loader = ConfigLoader()
            config = loader.load()
            
            assert config.ghl.location_id == "test_location"
            assert config.ghl.api_key == "test_key"
            assert config.ghl.schema_key == "test_schema"
            assert config.flask.host == "127.0.0.1"
            assert config.flask.port == 8000
            assert config.flask.debug is False
            assert config.logging.level == "DEBUG"


class TestValidators:
    """Test data validation functionality."""
    
    def test_vehicle_data_processor(self):
        """Test vehicle data extraction and validation."""
        processor = VehicleDataProcessor()
        
        # Test data extraction
        raw_data = {
            "stock_number": "12345",
            "make": "Toyota",
            "model": "Camry",
            "year": 2023,
            "irrelevant_field": "should_be_filtered"
        }
        
        properties = processor.extract_properties(raw_data)
        
        assert "stock_number" in properties
        assert "make" in properties
        assert "model" in properties
        assert "year" in properties
        assert "irrelevant_field" not in properties
        assert properties["stock_number"] == "12345"  # Should be string
    
    def test_validation_errors(self):
        """Test validation error handling."""
        processor = VehicleDataProcessor()
        
        # Test empty properties
        with pytest.raises(ValidationError):
            processor.validate_properties({})
        
        # Test missing stock_number
        with pytest.raises(ValidationError):
            processor.validate_properties({"make": "Toyota"})
        
        # Test invalid year
        with pytest.raises(ValidationError):
            processor.validate_properties({"stock_number": "123", "year": "invalid"})
    
    def test_request_payload_validation(self):
        """Test request payload validation."""
        # Valid payload
        valid_data = {"row": {"stock_number": "123"}}
        result = validate_request_payload(valid_data)
        assert result == {"stock_number": "123"}
        
        # Invalid payloads
        with pytest.raises(ValidationError):
            validate_request_payload({})  # Missing row
        
        with pytest.raises(ValidationError):
            validate_request_payload({"row": {}})  # Empty row
        
        with pytest.raises(ValidationError):
            validate_request_payload({"row": "not_dict"})  # Row not dict


if __name__ == "__main__":
    pytest.main([__file__])