"""Abstract interfaces for dependency inversion.

This module defines interfaces that allow for loose coupling and easy testing.
Follows the Dependency Inversion and Interface Segregation principles.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class RecordSearchResult:
    """Container for record search results."""
    
    def __init__(self, records: list, total_count: int = None):
        self.records = records
        self.total_count = total_count or len(records)
    
    @property
    def found(self) -> bool:
        """Check if any records were found."""
        return len(self.records) > 0
    
    @property
    def first_record(self) -> Optional[Dict[str, Any]]:
        """Get the first record if available."""
        return self.records[0] if self.records else None


class RecordService(ABC):
    """Abstract interface for record management services.
    
    This interface allows different implementations (GHL, Salesforce, etc.)
    to be used interchangeably, following the Dependency Inversion Principle.
    """
    
    @abstractmethod
    def search_by_identifier(self, identifier: str, identifier_field: str = "stock_number") -> RecordSearchResult:
        """Search for records by identifier.
        
        Args:
            identifier: The identifier value to search for.
            identifier_field: The field name to search in.
            
        Returns:
            RecordSearchResult: Search results.
        """
        pass
    
    @abstractmethod
    def update_record(self, record_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing record.
        
        Args:
            record_id: The ID of the record to update.
            properties: The properties to update.
            
        Returns:
            Dict containing the update response.
        """
        pass
    
    @abstractmethod
    def create_record(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record.
        
        Args:
            properties: The properties for the new record.
            
        Returns:
            Dict containing the creation response.
        """
        pass


class DataProcessor(ABC):
    """Abstract interface for data processing.
    
    Allows different data transformation strategies to be implemented.
    """
    
    @abstractmethod
    def extract_properties(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant properties from raw data.
        
        Args:
            raw_data: Raw input data.
            
        Returns:
            Dict containing extracted properties.
        """
        pass
    
    @abstractmethod
    def validate_properties(self, properties: Dict[str, Any]) -> bool:
        """Validate extracted properties.
        
        Args:
            properties: Properties to validate.
            
        Returns:
            True if valid, raises exception if invalid.
        """
        pass


class LoggerProtocol(ABC):
    """Protocol for logging services."""
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        pass
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        pass