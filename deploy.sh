#!/bin/bash

# Deployment Script for GHL Integration Service

set -e

PROJECT_DIR="/opt/livekit/google_sheets_to_ghl"
SERVICE_NAME="ghl-integration"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

cd "$PROJECT_DIR" || {
    print_error "Cannot change to project directory: $PROJECT_DIR"
    exit 1
}

print_status "Starting deployment..."

# Check if .env exists
if [ ! -f ".env" ]; then
    print_error ".env file not found! Please create it from .env.example"
    exit 1
fi

# Install dependencies
print_status "Installing dependencies..."
uv sync

# Run tests
print_status "Running tests..."
if uv run pytest tests/ -v; then
    print_success "All tests passed!"
else
    print_error "Tests failed! Deployment aborted."
    exit 1
fi

# Check if PM2 is available
if command -v pm2 &> /dev/null; then
    print_status "Deploying with PM2..."
    
    # Stop existing service if running
    pm2 stop $SERVICE_NAME 2>/dev/null || true
    
    # Start service
    pm2 start ecosystem.config.js
    
    # Save PM2 config
    pm2 save
    
    print_success "Service deployed with PM2!"
    
    # Test the deployment
    sleep 3
    print_status "Testing deployment..."
    
    if curl -f -s http://localhost:5020/health > /dev/null; then
        print_success "Health check passed! Service is running."
        curl -s http://localhost:5020/ | python3 -m json.tool
    else
        print_error "Health check failed!"
        pm2 logs $SERVICE_NAME --lines 10
        exit 1
    fi
    
else
    print_error "PM2 not found. Install it with: npm install -g pm2"
    print_status "You can also use systemd service: sudo cp ghl-integration.service /etc/systemd/system/"
    exit 1
fi

print_success "Deployment completed successfully!"
print_status "Use './pm2.sh status' to check service status"
print_status "Use './pm2.sh logs' to view logs"