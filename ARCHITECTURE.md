# Architecture Documentation

## Overview

This application has been refactored to follow SOLID principles and provide a modular, maintainable structure that supports future growth.

## SOLID Principles Implementation

### 1. Single Responsibility Principle (SRP)
Each module has a single, well-defined responsibility:

- **Config Module**: Configuration management only
- **Services Module**: External API operations only  
- **Utils Module**: Utility functions (logging, validation) only
- **API Module**: HTTP request/response handling only
- **Core Module**: Interfaces and shared components only

### 2. Open/Closed Principle (OCP)
The system is open for extension but closed for modification:

- New record services can be added by implementing `RecordService` interface
- New data processors can be added by implementing `DataProcessor` interface
- New logging strategies can be implemented via `LoggerProtocol`

### 3. Liskov Substitution Principle (LSP)
Any implementation of an interface can be substituted without breaking functionality:

- `GHLRecordService` can be replaced with `SalesforceRecordService`
- `VehicleDataProcessor` can be replaced with other data processors
- `StructuredLogger` can be replaced with other logger implementations

### 4. Interface Segregation Principle (ISP)
Interfaces are focused and client-specific:

- `RecordService`: Only record operations
- `DataProcessor`: Only data processing operations
- `LoggerProtocol`: Only logging operations

### 5. Dependency Inversion Principle (DIP)
High-level modules don't depend on low-level modules; both depend on abstractions:

- Controllers depend on service interfaces, not concrete implementations
- Services are injected via the dependency container
- Configuration is injected, not hardcoded

## Project Structure

```
src/
├── __init__.py                 # Package metadata
├── app.py                      # Application factory with DI container
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuration management
├── core/
│   ├── __init__.py
│   ├── interfaces.py           # Abstract interfaces for DIP
│   └── exceptions.py           # Custom exceptions
├── services/
│   ├── __init__.py
│   └── ghl_service.py         # GHL API service implementation
├── utils/
│   ├── __init__.py
│   ├── logging.py             # Logging utilities
│   └── validators.py          # Data validation
└── api/
    ├── __init__.py
    ├── routes.py              # Flask routes and controllers
    └── middleware.py          # Request/response middleware
```

## Key Components

### Configuration System (`src/config/`)
- **ConfigLoader**: Loads and validates environment variables
- **AppConfig**: Immutable configuration container with typed dataclasses
- **Validation**: Ensures required configuration is present

### Service Layer (`src/services/`)
- **GHLRecordService**: Implements RecordService interface for GHL API
- **Extensible**: New services can be added without changing existing code
- **Error Handling**: Proper exception hierarchy for different failure modes

### Utilities (`src/utils/`)
- **StructuredLogger**: Request-aware logging with proper context
- **VehicleDataProcessor**: Data extraction and validation for vehicle records
- **Validators**: Input validation with detailed error messages

### API Layer (`src/api/`)
- **Controllers**: Handle HTTP concerns, delegate business logic to services
- **Middleware**: Request logging, timing, and error handling
- **Routes**: Clean separation of HTTP routing from business logic

### Core Abstractions (`src/core/`)
- **Interfaces**: Abstract base classes for all major components
- **Exceptions**: Custom exception hierarchy for proper error handling
- **Data Containers**: Type-safe data transfer objects

## Dependency Injection

The `DependencyContainer` class manages all dependencies:

```python
container = DependencyContainer(config)
logger = container.logger                    # Singleton
record_service = container.record_service    # GHLRecordService instance
data_processor = container.data_processor    # VehicleDataProcessor instance
```

## Testing Strategy

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Configuration Tests**: Verify environment variable handling
- **Validation Tests**: Test data processing and validation logic

## Benefits of This Architecture

1. **Maintainability**: Clear separation of concerns makes code easier to understand and modify
2. **Testability**: Dependency injection enables easy mocking and unit testing
3. **Scalability**: New features can be added without modifying existing code
4. **Flexibility**: Different implementations can be swapped without changing business logic
5. **Error Handling**: Comprehensive exception hierarchy provides clear error reporting
6. **Configuration**: Environment-based configuration with validation
7. **Logging**: Structured logging with request tracing

## Future Extensions

The architecture supports easy addition of:

- **New Record Services**: Implement `RecordService` for Salesforce, HubSpot, etc.
- **New Data Processors**: Handle different data formats or validation rules
- **Authentication**: Add middleware for API key validation
- **Caching**: Add caching layer to service implementations
- **Monitoring**: Add metrics collection and health checks
- **Background Jobs**: Add async task processing
- **Database**: Add persistence layer for auditing or caching

## Migration Guide

The refactored application maintains backwards compatibility:

- `app.py` still works as before (imports from modular structure)
- `main.py` uses the new application factory
- Environment variables remain the same
- API endpoints are unchanged

## Running the Application

```bash
# Using the new modular structure
python main.py

# Using backwards compatible entry point
python app.py

# Running tests
uv run pytest tests/
```