# Google Sheets to GHL Integration

A Flask application that ingests vehicle data and syncs it with GoHighLevel (GHL) custom objects.

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

```bash
python app.py
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
  "response": { ... }
}
```

## Fields of Interest

The following fields are synced with GHL:
- stock_number
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
