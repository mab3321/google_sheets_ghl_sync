#!/bin/bash

# PM2 Management Script for GHL Integration Service

PROJECT_DIR="/opt/livekit/google_sheets_to_ghl"
SERVICE_NAME="ghl-integration"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_pm2() {
    if ! command -v pm2 &> /dev/null; then
        print_error "PM2 is not installed. Install it with: npm install -g pm2"
        exit 1
    fi
}

# Change to project directory
cd "$PROJECT_DIR" || {
    print_error "Cannot change to project directory: $PROJECT_DIR"
    exit 1
}

check_pm2

case "${1:-help}" in
    start)
        print_status "Starting $SERVICE_NAME service..."
        pm2 start ecosystem.config.js
        print_success "Service started. Use 'pm2 logs $SERVICE_NAME' to view logs."
        ;;
    
    stop)
        print_status "Stopping $SERVICE_NAME service..."
        pm2 stop $SERVICE_NAME
        print_success "Service stopped."
        ;;
    
    restart)
        print_status "Restarting $SERVICE_NAME service..."
        pm2 restart $SERVICE_NAME
        print_success "Service restarted."
        ;;
    
    reload)
        print_status "Reloading $SERVICE_NAME service with zero downtime..."
        pm2 reload $SERVICE_NAME
        print_success "Service reloaded."
        ;;
    
    delete)
        print_status "Deleting $SERVICE_NAME service from PM2..."
        pm2 delete $SERVICE_NAME
        print_success "Service deleted from PM2."
        ;;
    
    status)
        print_status "Checking service status..."
        pm2 status $SERVICE_NAME
        ;;
    
    logs)
        print_status "Showing logs for $SERVICE_NAME..."
        pm2 logs $SERVICE_NAME
        ;;
    
    monit)
        print_status "Opening PM2 monitoring dashboard..."
        pm2 monit
        ;;
    
    health)
        print_status "Checking service health..."
        if curl -f -s http://localhost:5020/health > /dev/null; then
            print_success "Service is healthy!"
            curl -s http://localhost:5020/health | python3 -m json.tool
        else
            print_error "Service health check failed!"
            exit 1
        fi
        ;;
    
    test)
        print_status "Testing root endpoint..."
        if curl -f -s http://localhost:5020/ > /dev/null; then
            print_success "Root endpoint is responding!"
            curl -s http://localhost:5020/ | python3 -m json.tool
        else
            print_error "Root endpoint test failed!"
            exit 1
        fi
        ;;
    
    setup)
        print_status "Setting up PM2 for production..."
        
        # Save PM2 process list
        pm2 save
        
        # Generate startup script
        print_status "Generating PM2 startup script..."
        pm2 startup
        
        print_warning "Please run the command shown above to enable PM2 auto-start on boot!"
        print_success "PM2 setup completed."
        ;;
    
    install-pm2)
        print_status "Installing PM2 globally..."
        if command -v npm &> /dev/null; then
            npm install -g pm2
            print_success "PM2 installed successfully!"
        else
            print_error "npm is not installed. Please install Node.js first."
            exit 1
        fi
        ;;
    
    help|*)
        echo "GHL Integration Service - PM2 Management Script"
        echo ""
        echo "Usage: $0 {command}"
        echo ""
        echo "Commands:"
        echo "  start       Start the service"
        echo "  stop        Stop the service"
        echo "  restart     Restart the service"
        echo "  reload      Reload the service with zero downtime"
        echo "  delete      Remove the service from PM2"
        echo "  status      Show service status"
        echo "  logs        Show service logs"
        echo "  monit       Open PM2 monitoring dashboard"
        echo "  health      Check service health endpoint"
        echo "  test        Test root endpoint"
        echo "  setup       Setup PM2 for production (save & startup)"
        echo "  install-pm2 Install PM2 globally"
        echo "  help        Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 start          # Start the service"
        echo "  $0 status         # Check if service is running"
        echo "  $0 logs           # View service logs"
        echo "  $0 health         # Test health endpoint"
        ;;
esac