"""Custom exceptions for the application."""


class AppException(Exception):
    """Base application exception."""
    pass


class ValidationError(AppException):
    """Raised when data validation fails."""
    pass


class ServiceError(AppException):
    """Raised when external service operations fail."""
    pass


class ConfigurationError(AppException):
    """Raised when configuration is invalid."""
    pass


class RecordNotFoundError(ServiceError):
    """Raised when a record is not found."""
    pass


class APIError(ServiceError):
    """Raised when API calls fail."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}