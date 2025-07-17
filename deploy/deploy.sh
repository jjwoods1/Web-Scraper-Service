#!/bin/bash

# Ubuntu Server Deployment Script for Unified Scraper API
# Run this script on your Ubuntu server

set -e

echo "🚀 Starting deployment of Unified Scraper API..."

# Configuration
PROJECT_NAME="unified-scraper-api"
DEPLOY_DIR="/opt/$PROJECT_NAME"
SERVICE_USER="scraper"
GITHUB_REPO="https://github.com/jjwoods1/Web-Scraper-Service.git"

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

# Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install required packages
print_status "Installing required packages..."
apt install -y \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx \
    curl \
    git \
    ufw \
    fail2ban \
    htop \
    unzip

# Start and enable Docker
print_status "Starting Docker service..."
systemctl start docker
systemctl enable docker

# Create service user
print_status "Creating service user..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/false -d $DEPLOY_DIR $SERVICE_USER
    usermod -aG docker $SERVICE_USER
fi

# Create deployment directory
print_status "Creating deployment directory..."
mkdir -p $DEPLOY_DIR
mkdir -p $DEPLOY_DIR/data
mkdir -p $DEPLOY_DIR/logs
mkdir -p $DEPLOY_DIR/nginx/ssl

# Clone or update repository
print_status "Cloning/updating repository..."
if [ -d "$DEPLOY_DIR/app" ]; then
    cd $DEPLOY_DIR/app
    git pull origin main
else
    git clone $GITHUB_REPO $DEPLOY_DIR/app
fi

# Copy deployment files
print_status "Setting up deployment files..."
cp $DEPLOY_DIR/app/deploy/* $DEPLOY_DIR/
cp $DEPLOY_DIR/app/deploy/.env.prod $DEPLOY_DIR/.env

# Generate API key
print_status "Generating production API key..."
API_KEY=$(openssl rand -hex 32)
sed -i "s/your-production-api-key-here/$API_KEY/" $DEPLOY_DIR/.env

# Generate secret key
print_status "Generating secret key..."
SECRET_KEY=$(openssl rand -hex 32)
sed -i "s/your-secret-key-here/$SECRET_KEY/" $DEPLOY_DIR/.env

# Set permissions
print_status "Setting permissions..."
chown -R $SERVICE_USER:$SERVICE_USER $DEPLOY_DIR
chmod -R 755 $DEPLOY_DIR
chmod 600 $DEPLOY_DIR/.env

# Configure firewall
print_status "Configuring firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp

# Configure fail2ban
print_status "Configuring fail2ban..."
systemctl start fail2ban
systemctl enable fail2ban

# Build and start services
print_status "Building and starting services..."
cd $DEPLOY_DIR
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to start
print_status "Waiting for services to start..."
sleep 30

# Test deployment
print_status "Testing deployment..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    print_status "✅ API health check passed"
else
    print_error "❌ API health check failed"
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
ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down
User=$SERVICE_USER
Group=$SERVICE_USER

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable scraper-api
systemctl start scraper-api

print_status "✅ Deployment completed successfully!"
echo
echo "================================================"
echo "🎉 Unified Scraper API is now running!"
echo "================================================"
echo
echo "📋 Deployment Summary:"
echo "  • API URL: http://$(curl -s ifconfig.me)/api/"
echo "  • Health Check: http://$(curl -s ifconfig.me)/health"
echo "  • API Key: $API_KEY"
echo "  • Logs: $DEPLOY_DIR/logs/"
echo "  • Data: $DEPLOY_DIR/data/"
echo
echo "🔧 Management Commands:"
echo "  • Start: systemctl start scraper-api"
echo "  • Stop: systemctl stop scraper-api"
echo "  • Status: systemctl status scraper-api"
echo "  • Logs: docker-compose -f $DEPLOY_DIR/docker-compose.prod.yml logs"
echo
echo "🔐 Security Notes:"
echo "  • Save your API key: $API_KEY"
echo "  • Configure SSL certificate for HTTPS"
echo "  • Update firewall rules as needed"
echo "  • Monitor logs regularly"
echo
echo "🌐 Next Steps:"
echo "  1. Configure your domain DNS to point to this server"
echo "  2. Set up SSL certificate with: certbot --nginx"
echo "  3. Update nginx configuration for your domain"
echo "  4. Test API endpoints with your applications"
echo

print_status "Deployment script completed!"