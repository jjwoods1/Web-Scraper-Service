#!/bin/bash

# Minimal Ubuntu Server Deployment Script for Unified Scraper API
# This script avoids conflicts with existing services

set -e

echo "🚀 Starting minimal deployment of Unified Scraper API..."

# Configuration
PROJECT_NAME="unified-scraper-api"
DEPLOY_DIR="/opt/$PROJECT_NAME"
SERVICE_USER="scraper"
GITHUB_REPO="https://github.com/jjwoods1/Web-Scraper-Service.git"
API_PORT="5001"  # Using port 5001 to avoid conflicts

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl start docker
    systemctl enable docker
else
    print_status "Docker is already installed"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_status "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    print_status "Docker Compose is already installed"
fi

# Create service user only if it doesn't exist
if ! id "$SERVICE_USER" &>/dev/null; then
    print_status "Creating service user..."
    useradd -r -s /bin/false -d $DEPLOY_DIR $SERVICE_USER
    usermod -aG docker $SERVICE_USER
else
    print_status "Service user already exists"
fi

# Create deployment directory
print_status "Creating deployment directory..."
mkdir -p $DEPLOY_DIR
mkdir -p $DEPLOY_DIR/data
mkdir -p $DEPLOY_DIR/logs

# Clone or update repository
print_status "Cloning/updating repository..."
if [ -d "$DEPLOY_DIR/app" ]; then
    cd $DEPLOY_DIR/app
    git pull origin main
else
    git clone $GITHUB_REPO $DEPLOY_DIR/app
fi

# Copy minimal deployment files
print_status "Setting up deployment files..."
cp $DEPLOY_DIR/app/deploy/docker-compose.minimal.yml $DEPLOY_DIR/docker-compose.yml
cp $DEPLOY_DIR/app/deploy/.env.prod $DEPLOY_DIR/.env

# Generate API key if not exists
if [ ! -f "$DEPLOY_DIR/.env" ] || ! grep -q "DEFAULT_API_KEY=" "$DEPLOY_DIR/.env"; then
    print_status "Generating production API key..."
    API_KEY=$(openssl rand -hex 32)
    sed -i "s/your-production-api-key-here/$API_KEY/" $DEPLOY_DIR/.env
    echo "DEFAULT_API_KEY=$API_KEY" >> $DEPLOY_DIR/.env
fi

# Set permissions
print_status "Setting permissions..."
chown -R $SERVICE_USER:$SERVICE_USER $DEPLOY_DIR
chmod -R 755 $DEPLOY_DIR
chmod 600 $DEPLOY_DIR/.env

# Stop existing container if running
print_status "Stopping existing container (if any)..."
cd $DEPLOY_DIR
docker-compose down 2>/dev/null || true

# Build and start services
print_status "Building and starting services..."
docker-compose build
docker-compose up -d

# Wait for services to start
print_status "Waiting for services to start..."
sleep 30

# Test deployment
print_status "Testing deployment..."
if curl -f http://localhost:$API_PORT/health > /dev/null 2>&1; then
    print_status "✅ API health check passed"
else
    print_error "❌ API health check failed"
    print_status "Checking logs..."
    docker-compose logs
    exit 1
fi

# Create systemd service
print_status "Creating systemd service..."
cat > /etc/systemd/system/scraper-api.service << EOF
[Unit]
Description=Unified Scraper API
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$DEPLOY_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable scraper-api
systemctl start scraper-api

# Get API key from environment file
API_KEY=$(grep "DEFAULT_API_KEY=" $DEPLOY_DIR/.env | cut -d'=' -f2)

print_status "✅ Minimal deployment completed successfully!"
echo
echo "================================================"
echo "🎉 Unified Scraper API is now running!"
echo "================================================"
echo
echo "📋 Deployment Summary:"
echo "  • API URL: http://$(hostname -I | awk '{print $1}'):$API_PORT/api/"
echo "  • Health Check: http://$(hostname -I | awk '{print $1}'):$API_PORT/health"
echo "  • API Key: $API_KEY"
echo "  • Port: $API_PORT (avoiding conflicts with existing services)"
echo "  • Logs: $DEPLOY_DIR/logs/"
echo "  • Data: $DEPLOY_DIR/data/"
echo
echo "🔧 Management Commands:"
echo "  • Start: systemctl start scraper-api"
echo "  • Stop: systemctl stop scraper-api"
echo "  • Status: systemctl status scraper-api"
echo "  • Logs: docker-compose -f $DEPLOY_DIR/docker-compose.yml logs"
echo "  • Update: cd $DEPLOY_DIR/app && git pull && cd $DEPLOY_DIR && docker-compose build && docker-compose up -d"
echo
echo "🔐 Security Notes:"
echo "  • Save your API key: $API_KEY"
echo "  • API is running on port $API_PORT to avoid conflicts"
echo "  • No nginx proxy (uses existing server setup)"
echo "  • No firewall changes made"
echo
echo "🌐 Test Commands:"
echo "  • Health: curl http://localhost:$API_PORT/health"
echo "  • Scrape: curl -X POST http://localhost:$API_PORT/api/scrape/urls -H 'Content-Type: application/json' -H 'X-API-Key: $API_KEY' -d '{\"url\": \"https://example.com\"}'"
echo

print_status "Minimal deployment script completed!"