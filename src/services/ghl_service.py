"""GoHighLevel API service implementation.

This module implements the RecordService interface for GHL API operations.
Follows Single Responsibility Principle by handling only GHL-specific operations.
"""

import requests
from typing import Any, Dict
from urllib.parse import urljoin

from ..core.interfaces import RecordService, RecordSearchResult, LoggerProtocol
from ..core.exceptions import APIError, ValidationError
from ..config.settings import GHLConfig


class GHLRecordService(RecordService):
    """GoHighLevel API service implementation.
    
    Implements the RecordService interface for GHL operations.
    Follows Single Responsibility and Open/Closed principles.
    """
    
    def __init__(self, config: GHLConfig, logger: LoggerProtocol):
        """Initialize GHL service.
        
        Args:
            config: GHL configuration.
            logger: Logger instance for dependency injection.
        """
        self.config = config
        self.logger = logger
        self._session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create configured requests session."""
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Version": "2021-07-28",
            "Authorization": f"Bearer {self.config.api_key}",
        })
        return session
    
    def search_by_identifier(self, identifier: str, identifier_field: str = "stock_number") -> RecordSearchResult:
        """Search for records by identifier.
        
        Args:
            identifier: The identifier value to search for.
            identifier_field: The field name to search in.
            
        Returns:
            RecordSearchResult: Search results.
            
        Raises:
            APIError: If the API request fails.
        """
        if not identifier:
            raise ValidationError(f"{identifier_field} cannot be empty")
        
        url = urljoin(self.config.base_url, f"objects/{self.config.schema_key}/records/search")
        payload = {
            "locationId": self.config.location_id,
            "page": 1,
            "pageLimit": 1,
            "query": str(identifier),
        }
        
        try:
            self.logger.debug(f"Searching for record with {identifier_field}={identifier}")
            response = self._session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            records = data.get("records", [])
            
            self.logger.debug(f"Search returned {len(records)} records")
            return RecordSearchResult(records)
            
        except requests.HTTPError as e:
            error_msg = f"Failed to search records: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg, status_code=e.response.status_code if e.response else None)
        except requests.RequestException as e:
            error_msg = f"Network error during record search: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg)
    
    def update_record(self, record_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing record.
        
        Args:
            record_id: The ID of the record to update.
            properties: The properties to update.
            
        Returns:
            Dict containing the update response.
            
        Raises:
            APIError: If the API request fails.
        """
        if not record_id:
            raise ValidationError("record_id cannot be empty")
        if not properties:
            raise ValidationError("properties cannot be empty")
        
        url = urljoin(
            self.config.base_url,
            f"objects/{self.config.schema_key}/records/{record_id}"
        )
        payload = {"properties": properties}
        params = {"locationId": self.config.location_id}
        
        try:
            self.logger.debug(
                f"Updating record {record_id} with {len(properties)} properties"
            )
            response = self._session.put(url, json=payload, params=params)
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f"Successfully updated record {record_id}")
            return data
            
        except requests.HTTPError as e:
            error_msg = f"Failed to update record {record_id}: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg, status_code=e.response.status_code if e.response else None)
        except requests.RequestException as e:
            error_msg = f"Network error during record update: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg)
    
    def create_record(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record.
        
        Args:
            properties: The properties for the new record.
            
        Returns:
            Dict containing the creation response.
            
        Raises:
            APIError: If the API request fails.
        """
        if not properties:
            raise ValidationError("properties cannot be empty")
        
        url = urljoin(self.config.base_url, f"objects/{self.config.schema_key}/records")
        payload = {
            "locationId": self.config.location_id,
            "properties": properties
        }
        
        try:
            self.logger.debug(f"Creating new record with {len(properties)} properties")
            response = self._session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            record_id = data.get("id")
            self.logger.info(f"Successfully created record {record_id}")
            return data
            
        except requests.HTTPError as e:
            error_msg = f"Failed to create record: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg, status_code=e.response.status_code if e.response else None)
        except requests.RequestException as e:
            error_msg = f"Network error during record creation: {e}"
            self.logger.error(error_msg)
            raise APIError(error_msg)