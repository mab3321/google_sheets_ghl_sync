"""Backwards compatibility entry point.

This file maintains backwards compatibility for direct execution of app.py
while using the new modular structure.
"""

from src.app import create_app, run_app

# Create app instance for external imports
app = create_app()

if __name__ == "__main__":
    run_app(app)
