# Google Sheets to GHL Integration

A Flask application that ingests vehicle data and syncs it with GoHighLevel (GHL) custom objects.

## Architecture

This application follows **SOLID principles** and implements a modular architecture for maintainability and extensibility. See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design documentation.

### Key Features
- 🏗️ **Modular Design**: Clean separation of concerns with dependency injection
- 🔒 **Type Safety**: Full type hints and validation
- 📊 **Structured Logging**: Request-aware logging with proper context
- ⚡ **Extensible**: Easy to add new services, processors, and features  
- 🧪 **Testable**: Comprehensive test coverage with mocking support
- 🔧 **Configurable**: Environment-based configuration with validation

## Project Structure

```
src/
├── config/          # Configuration management
├── core/            # Interfaces and shared components  
├── services/        # External API services (GHL, etc.)
├── utils/           # Utilities (logging, validation)
├── api/             # Flask routes and middleware
└── app.py           # Application factory
```

## Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

### Required Environment Variables

- `GHL_LOCATION_ID`: Your GHL location ID
- `GHL_API_KEY`: Your GHL API key

### Optional Environment Variables

- `GHL_SCHEMA_KEY`: Schema key for custom objects (default: `custom_objects.vehicles`)
- `FLASK_HOST`: Flask host (default: `0.0.0.0`)
- `FLASK_PORT`: Flask port (default: `5000`)
- `FLASK_DEBUG`: Enable debug mode (default: `false`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

## Installation

```bash
uv sync
```

## Running

### Development
```bash
# Main entry point (recommended)
python main.py

# Backwards compatible entry point
python app.py

# With uv
uv run python main.py
```

### Production with PM2

1. **Install PM2** (if not already installed):
```bash
./pm2.sh install-pm2
```

2. **Deploy the service**:
```bash
./deploy.sh
```

3. **Manage the service**:
```bash
./pm2.sh start       # Start the service
./pm2.sh stop        # Stop the service
./pm2.sh restart     # Restart the service
./pm2.sh status      # Check status
./pm2.sh logs        # View logs
./pm2.sh health      # Check health endpoint
./pm2.sh test        # Test root endpoint
```

4. **Setup auto-start** (run once):
```bash
./pm2.sh setup
```

### Alternative: Systemd Service

```bash
# Copy service file
sudo cp ghl-integration.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable ghl-integration
sudo systemctl start ghl-integration

# Check status
sudo systemctl status ghl-integration
```

## Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_basic.py -v

# Run with coverage
uv run pytest --cov=src tests/
```

## API Endpoints

### POST /ingest

Ingests vehicle data and updates or creates records in GHL.

**Request Body:**
```json
{
  "row": {
    "stock_number": "12345",
    "make": "Toyota",
    "model": "Camry",
    "year": 2023,
    // ... other vehicle fields
  }
}
```

**Response:**
```json
{
  "status": "updated",
  "record_id": "abc123",
  "stock_number": "12345",
  "response": { ... }
}
```

### GET /health

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "service": "google-sheets-to-ghl",
  "version": "0.1.0"
}
```

## Fields of Interest

The following fields are synced with GHL:
- stock_number *(required)*
- make
- model
- trim
- year
- vehicle_type
- drive
- transmission
- cylinders
- fuel_type
- colour
- vin

## Development

### Adding New Features

The modular architecture makes it easy to extend:

1. **New Record Services**: Implement `RecordService` interface
2. **New Data Processors**: Implement `DataProcessor` interface  
3. **New Validators**: Add to `utils/validators.py`
4. **New Routes**: Add to `api/routes.py`

### Error Handling

The application uses a comprehensive exception hierarchy:

- `ValidationError`: Data validation failures
- `APIError`: External API failures
- `ServiceError`: Service-level errors
- `ConfigurationError`: Configuration issues

### Logging

Structured logging with request context:

```python
logger.info("Processing request", stock_number="12345", record_count=10)
```

## Dependencies

- **Flask**: Web framework
- **requests**: HTTP client
- **python-dotenv**: Environment variable loading
- **pytest**: Testing framework (dev)

## License

[Add your license here]
