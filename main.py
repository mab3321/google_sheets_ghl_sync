"""Main entry point for the Google Sheets to GHL integration service.

This file serves as the entry point for running the application.
It imports the modular application factory and runs it.
"""

from src.app import create_app, run_app

if __name__ == "__main__":
    app = create_app()
    run_app(app)
