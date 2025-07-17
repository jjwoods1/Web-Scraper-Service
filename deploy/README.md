# Ubuntu Server Deployment Guide

This guide will help you deploy the Unified Scraper API to your Ubuntu server with Docker, Nginx, and SSL support.

## 🚀 Quick Deployment

### Option 1: Automated Deployment (Recommended)

1. **Upload deployment files to your server**:
   ```bash
   scp -r deploy/ user@your-server-ip:/tmp/
   ```

2. **Run the deployment script**:
   ```bash
   ssh user@your-server-ip
   sudo chmod +x /tmp/deploy/deploy.sh
   sudo /tmp/deploy/deploy.sh
   ```

3. **Save the generated API key** displayed at the end of the deployment.

### Option 2: Manual Deployment

Follow the step-by-step instructions below for manual deployment.

## 📋 Prerequisites

- Ubuntu 18.04 or later
- Root or sudo access
- At least 1GB RAM
- 10GB free disk space
- Domain name (optional, for SSL)

## 🛠️ Manual Deployment Steps

### Step 1: Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install Dependencies
```bash
sudo apt install -y docker.io docker-compose nginx certbot python3-certbot-nginx curl git ufw fail2ban
```

### Step 3: Start Docker
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Step 4: Create Service User
```bash
sudo useradd -r -s /bin/false -d /opt/unified-scraper-api scraper
sudo usermod -aG docker scraper
```

### Step 5: Clone Repository
```bash
sudo mkdir -p /opt/unified-scraper-api
sudo git clone https://github.com/jjwoods1/Web-Scraper-Service.git /opt/unified-scraper-api/app
```

### Step 6: Set Up Environment
```bash
sudo cp /opt/unified-scraper-api/app/deploy/.env.prod /opt/unified-scraper-api/.env
sudo cp /opt/unified-scraper-api/app/deploy/docker-compose.prod.yml /opt/unified-scraper-api/
sudo cp -r /opt/unified-scraper-api/app/deploy/nginx /opt/unified-scraper-api/
```

### Step 7: Configure Environment Variables
```bash
sudo nano /opt/unified-scraper-api/.env
```

Update these values:
- `DEFAULT_API_KEY`: Generate a secure API key
- `SECRET_KEY`: Generate a secure secret key
- `ALLOWED_ORIGINS`: Set to your domain or specific origins

### Step 8: Set Permissions
```bash
sudo chown -R scraper:scraper /opt/unified-scraper-api
sudo chmod -R 755 /opt/unified-scraper-api
sudo chmod 600 /opt/unified-scraper-api/.env
```

### Step 9: Configure Firewall
```bash
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Step 10: Deploy with Docker Compose
```bash
cd /opt/unified-scraper-api
sudo docker-compose -f docker-compose.prod.yml build
sudo docker-compose -f docker-compose.prod.yml up -d
```

### Step 11: Test Deployment
```bash
curl http://localhost:5000/health
```

## 🔒 SSL Configuration (Optional but Recommended)

### Step 1: Configure Your Domain
Point your domain's DNS A record to your server's IP address.

### Step 2: Update Nginx Configuration
```bash
sudo nano /opt/unified-scraper-api/nginx/nginx.conf
```

Replace `your-domain.com` with your actual domain in the HTTPS server block.

### Step 3: Obtain SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com
```

### Step 4: Restart Services
```bash
cd /opt/unified-scraper-api
sudo docker-compose -f docker-compose.prod.yml restart
```

## 🔧 Management Commands

### Service Management
```bash
# Start services
sudo docker-compose -f /opt/unified-scraper-api/docker-compose.prod.yml up -d

# Stop services
sudo docker-compose -f /opt/unified-scraper-api/docker-compose.prod.yml down

# View logs
sudo docker-compose -f /opt/unified-scraper-api/docker-compose.prod.yml logs -f

# Check status
sudo docker-compose -f /opt/unified-scraper-api/docker-compose.prod.yml ps
```

### API Key Management
```bash
cd /opt/unified-scraper-api/app
sudo python3 key_manager.py generate "My New Key"
sudo python3 key_manager.py list
sudo python3 key_manager.py revoke "key-id"
```

### Update Application
```bash
cd /opt/unified-scraper-api/app
sudo git pull origin main
cd /opt/unified-scraper-api
sudo docker-compose -f docker-compose.prod.yml build
sudo docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Monitoring

### Log Files
- Application logs: `/opt/unified-scraper-api/logs/`
- Nginx logs: `/opt/unified-scraper-api/logs/nginx/`
- Docker logs: `sudo docker-compose logs`

### Health Check
```bash
curl http://your-domain.com/health
```

### System Resources
```bash
htop
sudo docker stats
```

## 🔐 Security Best Practices

1. **Change default API key**: Generate a strong, unique API key
2. **Enable SSL**: Use Let's Encrypt for free SSL certificates
3. **Configure fail2ban**: Protect against brute force attacks
4. **Regular updates**: Keep system and dependencies updated
5. **Monitor logs**: Regularly check application and system logs
6. **Backup data**: Regular backups of `/opt/unified-scraper-api/data/`

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   sudo netstat -tulpn | grep :80
   sudo systemctl stop apache2  # If Apache is running
   ```

2. **Docker permission denied**:
   ```bash
   sudo usermod -aG docker $USER
   # Log out and log back in
   ```

3. **API not responding**:
   ```bash
   sudo docker-compose -f /opt/unified-scraper-api/docker-compose.prod.yml logs
   ```

4. **SSL certificate issues**:
   ```bash
   sudo certbot renew --dry-run
   ```

### Log Analysis
```bash
# Application logs
sudo tail -f /opt/unified-scraper-api/logs/scraper.log

# Nginx access logs
sudo tail -f /opt/unified-scraper-api/logs/nginx/access.log

# Nginx error logs
sudo tail -f /opt/unified-scraper-api/logs/nginx/error.log
```

## 📝 API Usage Examples

### Health Check
```bash
curl http://your-domain.com/health
```

### URL Scraping
```bash
curl -X POST "http://your-domain.com/api/scrape/urls" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"url": "https://example.com"}'
```

### Text Scraping
```bash
curl -X POST "http://your-domain.com/api/scrape/text" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"url": "https://example.com"}'
```

## 🔄 Backup and Recovery

### Create Backup
```bash
sudo tar -czf scraper-backup-$(date +%Y%m%d).tar.gz /opt/unified-scraper-api/
```

### Restore Backup
```bash
sudo tar -xzf scraper-backup-YYYYMMDD.tar.gz -C /
sudo chown -R scraper:scraper /opt/unified-scraper-api
```

## 📞 Support

For issues and support:
- Check the logs first
- Review this documentation
- Open an issue on GitHub
- Contact your system administrator

## 🎉 Success!

Your Unified Scraper API is now deployed and ready for production use!