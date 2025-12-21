"""Data validation utilities.

This module provides data validation and processing functionality.
Follows Single Responsibility Principle.
"""

from typing import Any, Dict, List

from ..core.interfaces import DataProcessor
from ..core.exceptions import ValidationError
from ..config.settings import config


class VehicleDataProcessor(DataProcessor):
    """Vehicle data processor implementation.
    
    Handles extraction and validation of vehicle data for GHL sync.
    """
    
    def __init__(self, fields_of_interest: List[str] = None):
        """Initialize processor.
        
        Args:
            fields_of_interest: List of fields to extract. Defaults to config fields.
        """
        from ..config.settings import ConfigLoader
        self.fields_of_interest = fields_of_interest or ConfigLoader.FIELDS_OF_INTEREST
    
    def extract_properties(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant properties from raw data.
        
        Args:
            raw_data: Raw input data from the request.
            
        Returns:
            Dict containing extracted and cleaned properties.
        """
        properties = {
            k: v for k, v in raw_data.items() 
            if k in self.fields_of_interest and v is not None
        }
        
        # Ensure stock_number is always a string (API requirement)
        if "stock_number" in properties:
            properties["stock_number"] = str(properties["stock_number"])
        
        # Clean and normalize other fields as needed
        for key, value in properties.items():
            if isinstance(value, str):
                properties[key] = value.strip()
        
        return properties
    
    def validate_properties(self, properties: Dict[str, Any]) -> bool:
        """Validate extracted properties.
        
        Args:
            properties: Properties to validate.
            
        Returns:
            True if valid.
            
        Raises:
            ValidationError: If validation fails.
        """
        if not properties:
            raise ValidationError("Properties cannot be empty")
        
        # Validate required fields
        required_fields = ["stock_number"]
        for field in required_fields:
            if field not in properties or not properties[field]:
                raise ValidationError(f"Required field '{field}' is missing or empty")
        
        # Validate data types
        if "year" in properties:
            year = properties["year"]
            if year is not None:
                try:
                    year_int = int(year)
                    if year_int < 1900 or year_int > 2030:
                        raise ValidationError(f"Year {year} is not in valid range (1900-2030)")
                except (ValueError, TypeError):
                    raise ValidationError(f"Year must be a valid integer, got: {year}")
        
        # Validate string lengths
        string_fields = ["make", "model", "trim", "colour", "vin"]
        for field in string_fields:
            if field in properties and properties[field]:
                value = str(properties[field])
                if len(value) > 100:  # Reasonable limit
                    raise ValidationError(f"Field '{field}' exceeds maximum length (100 characters)")
        
        # VIN validation (basic)
        if "vin" in properties and properties["vin"]:
            vin = str(properties["vin"]).upper().strip()
            if len(vin) not in [11, 17]:  # Allow both partial and full VINs
                raise ValidationError(f"VIN length must be 11 or 17 characters, got: {len(vin)}")
            properties["vin"] = vin  # Normalize to uppercase
        
        return True


def validate_request_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate incoming request payload.
    
    Args:
        data: Request payload data.
        
    Returns:
        Validated row data.
        
    Raises:
        ValidationError: If payload is invalid.
    """
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object")
    
    if "row" not in data:
        raise ValidationError("Request payload must contain 'row' field")
    
    row = data["row"]
    if not isinstance(row, dict):
        raise ValidationError("'row' field must be a JSON object")
    
    if not row:
        raise ValidationError("'row' field cannot be empty")
    
    return row