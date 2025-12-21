"""Flask routes for the application.

This module contains all API endpoints. Follows Single Responsibility Principle
by handling only HTTP request/response concerns.
"""

import time
from flask import Blueprint, request, jsonify, g
from typing import Dict, Any

from ..core.interfaces import RecordService, DataProcessor, LoggerProtocol
from ..core.exceptions import ValidationError, APIError, ServiceError
from ..utils.validators import validate_request_payload


class IngestController:
    """Controller for data ingestion endpoints.
    
    Handles HTTP concerns while delegating business logic to services.
    Follows Single Responsibility and Dependency Inversion principles.
    """
    
    def __init__(
        self,
        record_service: RecordService,
        data_processor: DataProcessor,
        logger: LoggerProtocol
    ):
        """Initialize controller with dependencies.
        
        Args:
            record_service: Service for record operations.
            data_processor: Service for data processing.
            logger: Logger for dependency injection.
        """
        self.record_service = record_service
        self.data_processor = data_processor
        self.logger = logger
    
    def ingest_data(self) -> tuple[Dict[str, Any], int]:
        """Handle data ingestion requests.
        
        Returns:
            Tuple of (response_data, status_code).
        """
        try:
            # Validate request
            data = request.get_json(silent=True) or {}
            row = validate_request_payload(data)
            
            # Process data
            properties = self.data_processor.extract_properties(row)
            self.data_processor.validate_properties(properties)
            
            stock_number = properties["stock_number"]
            
            self.logger.info(
                f"Processing stock_number={stock_number} with {len(properties)} properties"
            )
            
            # Search for existing record
            search_result = self.record_service.search_by_identifier(stock_number)
            
            if search_result.found:
                # Update existing record
                record_id = search_result.first_record["id"]
                self.logger.info(f"Updating existing record {record_id}")
                
                updated = self.record_service.update_record(record_id, properties)
                
                return {
                    "status": "updated",
                    "record_id": record_id,
                    "stock_number": stock_number,
                    "response": updated
                }, 200
            else:
                # Record not found
                self.logger.info(f"Record not found for stock_number={stock_number}")
                
                return {
                    "status": "not_found",
                    "stock_number": stock_number,
                    "message": "Record not found. Create operation not implemented."
                }, 404
        
        except ValidationError as e:
            self.logger.warning(f"Validation error: {str(e)}")
            return {"error": f"Validation error: {str(e)}"}, 400
        
        except APIError as e:
            self.logger.error(f"API error: {str(e)}")
            status_code = e.status_code or 502
            return {"error": f"External API error: {str(e)}"}, status_code
        
        except ServiceError as e:
            self.logger.error(f"Service error: {str(e)}")
            return {"error": f"Service error: {str(e)}"}, 503
        
        except Exception as e:
            # Calculate duration for logging
            duration_ms = 0
            if hasattr(g, "start_time"):
                duration_ms = int((time.time() - g.start_time) * 1000)
            
            self.logger.exception(
                f"Unhandled error in ingest: {str(e)}",
                duration=duration_ms
            )
            return {"error": "Internal server error"}, 500


def create_routes(
    record_service: RecordService,
    data_processor: DataProcessor,
    logger: LoggerProtocol
) -> Blueprint:
    """Create Flask blueprint with all routes.
    
    Args:
        record_service: Service for record operations.
        data_processor: Service for data processing.
        logger: Logger instance.
        
    Returns:
        Flask Blueprint with configured routes.
    """
    bp = Blueprint("api", __name__)
    controller = IngestController(record_service, data_processor, logger)
    
    @bp.route("/ingest", methods=["POST"])
    def ingest():
        """POST /ingest endpoint."""
        response_data, status_code = controller.ingest_data()
        return jsonify(response_data), status_code
    
    @bp.route("/health", methods=["GET"])
    def health():
        """GET /health endpoint for health checks."""
        return jsonify({
            "status": "healthy",
            "service": "google-sheets-to-ghl",
            "version": "0.1.0"
        }), 200
    
    return bp