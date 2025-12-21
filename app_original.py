import logging
import os
import time
import uuid
from typing import Any, Dict, Optional, Tuple

import requests
from flask import Flask, request, jsonify, g
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# GHL config from environment variables
LOCATION_ID = os.getenv("GHL_LOCATION_ID")
SCHEMA_KEY = os.getenv("GHL_SCHEMA_KEY", "custom_objects.vehicles")
API_KEY = os.getenv("GHL_API_KEY")

# Validate required environment variables
if not LOCATION_ID:
    raise ValueError("GHL_LOCATION_ID environment variable is required")
if not API_KEY:
    raise ValueError("GHL_API_KEY environment variable is required")

# Only these fields will be synced
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


def setup_logging(level: Optional[str] = None) -> logging.Logger:
    """Configure and return a module-level logger with console and file handlers.

    Level can be overridden by the `LOG_LEVEL` environment variable or the `level`
    argument. Defaults to INFO.
    """
    logger = logging.getLogger("dealerpull.flask")
    if logger.handlers:
        # Already configured
        return logger

    resolved_level_name = (level or os.getenv("LOG_LEVEL") or "INFO").upper()
    resolved_level = getattr(logging, resolved_level_name, logging.INFO)
    logger.setLevel(resolved_level)

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s "
            "[req_id=%(request_id)s duration=%(duration)sms]"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(resolved_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler (rotating small file in the same directory)
    try:
        from logging.handlers import RotatingFileHandler

        log_file = os.path.join(os.path.dirname(__file__), "test_flask.log")
        fh = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
        fh.setLevel(resolved_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception:
        # If file handler fails (permissions, etc.), proceed with console only
        pass

    # Provide default values for custom fields to avoid formatting errors
    class RequestContextFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            if not hasattr(record, "request_id"):
                record.request_id = "-"
            if not hasattr(record, "duration"):
                record.duration = 0
            return True

    logger.addFilter(RequestContextFilter())
    return logger


logger = setup_logging()


def extract_properties(row: Dict[str, Any]) -> Dict[str, Any]:
    """Return only the fields of interest from the incoming row, ensuring proper types."""
    properties = {k: v for k, v in row.items() if k in FIELDS_OF_INTEREST}

    # Ensure stock_number is always a string (API requirement)
    if "stock_number" in properties and properties["stock_number"] is not None:
        properties["stock_number"] = str(properties["stock_number"])

    return properties


def build_headers(api_key: str) -> Dict[str, str]:
    """Build default headers for LeadConnector API requests."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Version": "2021-07-28",
        "Authorization": f"Bearer {api_key}",
    }


def search_record(stock_number: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """Search for an existing record by stock number."""
    url = f"https://services.leadconnectorhq.com/objects/{SCHEMA_KEY}/records/search"
    payload = {
        "locationId": LOCATION_ID,
        "page": 1,
        "pageLimit": 1,
        "query": f"{stock_number}",
    }

    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()


def update_record(
    record_id: str, properties: Dict[str, Any], headers: Dict[str, str]
) -> Dict[str, Any]:
    """Update an existing record's properties by record ID."""
    url = f"https://services.leadconnectorhq.com/objects/{SCHEMA_KEY}/records/{record_id}?locationId={LOCATION_ID}"
    payload = {"properties": properties}

    # Log payload metadata without exposing sensitive data
    try:
        from flask import g

        request_id = getattr(g, "request_id", "-")
    except (RuntimeError, AttributeError):
        # Outside of Flask request context
        request_id = "-"

    logger.debug(
        "Sending PUT request to update record_id=%s with %d properties (keys: %s)",
        record_id,
        len(properties),
        list(properties.keys()),
        extra={"request_id": request_id},
    )

    resp = requests.put(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()


def create_app() -> Flask:
    """Application factory that sets up routes, hooks, and logging."""
    app = Flask(__name__)

    @app.before_request
    def _before_request():
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        g.start_time = time.time()
        logger.info(
            "Incoming request %s %s",
            request.method,
            request.path,
            extra={"request_id": g.request_id},
        )

    @app.after_request
    def _after_request(response):
        duration_ms = int((time.time() - getattr(g, "start_time", time.time())) * 1000)
        extra = {"request_id": getattr(g, "request_id", "-"), "duration": duration_ms}
        logger.info(
            "Response %s %s status=%s duration=%sms",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
            extra=extra,
        )
        return response

    @app.route("/ingest", methods=["POST"])
    def ingest():
        try:
            data = request.get_json(silent=True) or {}
            if "row" not in data:
                logger.warning(
                    "Invalid payload: missing 'row'", extra={"request_id": g.request_id}
                )
                return jsonify({"error": "Invalid payload"}), 400

            row = data["row"]
            stock_number = row.get("stock_number")
            if not stock_number:
                logger.warning(
                    "Missing required field 'stock_number'",
                    extra={"request_id": g.request_id},
                )
                return jsonify({"error": "stock_number is required"}), 400

            headers = build_headers(API_KEY)
            # Log only metadata to avoid sensitive values
            properties = extract_properties(row)
            logger.info(
                "Processing stock_number=%s with %d properties",
                stock_number,
                len(properties),
                extra={"request_id": g.request_id},
            )

            search_data = search_record(stock_number, headers)
            records = search_data.get("records", [])
            if records:
                record_id = records[0]["id"]
                logger.info(
                    "Updating record_id=%s",
                    record_id,
                    extra={"request_id": g.request_id},
                )
                updated = update_record(record_id, properties, headers)
                return jsonify(
                    {"status": "updated", "record_id": record_id, "response": updated}
                )

            logger.info(
                "Record not found for stock_number=%s",
                stock_number,
                extra={"request_id": g.request_id},
            )
            return jsonify({"status": "not_found", "stock_number": stock_number})

        except requests.HTTPError as http_err:
            duration_ms = int(
                (time.time() - getattr(g, "start_time", time.time())) * 1000
            )
            extra = {
                "request_id": getattr(g, "request_id", "-"),
                "duration": duration_ms,
            }
            logger.exception(
                "HTTP error while processing ingest: %s", http_err, extra=extra
            )
            return jsonify({"error": str(http_err)}), 502
        except Exception as e:
            duration_ms = int(
                (time.time() - getattr(g, "start_time", time.time())) * 1000
            )
            extra = {
                "request_id": getattr(g, "request_id", "-"),
                "duration": duration_ms,
            }
            logger.exception(
                "Unhandled error while processing ingest: %s", e, extra=extra
            )
            return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()


def _env_bool(name: str, default: bool = False) -> bool:
    """Read a boolean from environment variables."""
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = _env_bool("FLASK_DEBUG", False)
    logger.info(
        "Starting Flask app on %s:%s debug=%s",
        host,
        port,
        debug,
        extra={"request_id": "startup", "duration": 0},
    )
    app.run(host=host, port=port, debug=debug)
