# Daily Tracker - Deployment Guide

**Version:** 1.0.0  
**Last Updated:** October 21, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Production Deployment](#production-deployment)
4. [Systemd Service](#systemd-service)
5. [Nginx Reverse Proxy](#nginx-reverse-proxy)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [Security Hardening](#security-hardening)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup & Restore](#backup--restore)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers deploying Daily Tracker to a production environment with:

- **Systemd service** - Auto-start, restart on failure
- **Nginx reverse proxy** - SSL termination, load balancing
- **SSL/TLS encryption** - Free Let's Encrypt certificates
- **Security hardening** - Firewall, rate limiting, secure headers
- **Monitoring** - Logging, health checks, alerts

### Deployment Architecture

```
Internet
    ↓
[Firewall - UFW]
    ↓
[Nginx :443] ← SSL/TLS
    ↓
[Tracker API :8000]
    ↓
[SQLite Database]
```

---

## Prerequisites

### Server Requirements

**Minimum Specifications:**
- **OS:** Ubuntu 22.04 LTS (or similar Linux)
- **CPU:** 1 vCPU
- **RAM:** 1 GB
- **Storage:** 10 GB SSD
- **Network:** Public IP address

**Recommended Specifications:**
- **CPU:** 2 vCPUs
- **RAM:** 2 GB
- **Storage:** 20 GB SSD

**Popular Hosting Providers:**
- DigitalOcean Droplet ($6/month)
- AWS EC2 t3.micro ($10/month)
- Linode Nanode ($5/month)
- Hetzner Cloud CX11 (€4/month)

### Software Requirements

- Python 3.12+
- Nginx 1.18+
- UFW (Uncomplicated Firewall)
- systemd
- certbot (for Let's Encrypt)

### Domain Name

For SSL/TLS, you'll need a domain name pointing to your server:

```bash
# Example DNS A record
tracker.yourdomain.com → 203.0.113.45
```

---

## Production Deployment

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    nginx \
    ufw \
    certbot \
    python3-certbot-nginx \
    git \
    curl

# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

### Step 2: Create Deployment User

```bash
# Create dedicated user for security
sudo useradd -m -s /bin/bash tracker
sudo usermod -aG sudo tracker

# Switch to tracker user
sudo su - tracker
```

### Step 3: Install Application

```bash
# Clone repository
cd /home/tracker
git clone https://github.com/yourusername/tracker.git
cd tracker

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .

# Initialize database
python scripts/init_db.py
```

### Step 4: Configure Application

```bash
# Set production configuration
tracker config set ai_provider openai
tracker config set openai_api_key "your-production-key"
tracker config set openai_model "gpt-4"

# Verify installation
tracker --version
```

### Step 5: Create Production User

```bash
# Create admin account via Python
python -c "
from tracker.core.database import SessionLocal
from tracker.core.auth import get_password_hash
from tracker.core.models import User
from datetime import datetime

db = SessionLocal()
user = User(
    username='admin',
    email='admin@yourdomain.com',
    hashed_password=get_password_hash('SECURE_PASSWORD_HERE'),
    created_at=datetime.utcnow()
)
db.add(user)
db.commit()
print(f'Created user: {user.username}')
"
```

---

## Systemd Service

### Create Service File

Create `/etc/systemd/system/tracker-api.service`:

```ini
[Unit]
Description=Daily Tracker API Server
After=network.target

[Service]
Type=simple
User=tracker
Group=tracker
WorkingDirectory=/home/tracker/tracker
Environment="PATH=/home/tracker/tracker/.venv/bin"
ExecStart=/home/tracker/tracker/.venv/bin/uvicorn tracker.api.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --workers 2 \
    --log-level info \
    --no-access-log

# Security
PrivateTmp=yes
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/home/tracker/tracker
ReadWritePaths=/home/tracker/.config/tracker

# Restart behavior
Restart=always
RestartSec=10
StartLimitBurst=5
StartLimitIntervalSec=60

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=tracker-api

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable tracker-api

# Start service
sudo systemctl start tracker-api

# Check status
sudo systemctl status tracker-api

# View logs
sudo journalctl -u tracker-api -f
```

### Service Management Commands

```bash
# Start service
sudo systemctl start tracker-api

# Stop service
sudo systemctl stop tracker-api

# Restart service
sudo systemctl restart tracker-api

# Reload after code changes
sudo systemctl restart tracker-api

# Check if running
sudo systemctl is-active tracker-api

# View logs (last 100 lines)
sudo journalctl -u tracker-api -n 100

# Follow logs in real-time
sudo journalctl -u tracker-api -f
```

---

## Nginx Reverse Proxy

### Create Nginx Configuration

Create `/etc/nginx/sites-available/tracker`:

```nginx
# Rate limiting zone
limit_req_zone $binary_remote_addr zone=tracker_limit:10m rate=10r/s;

# Upstream (API server)
upstream tracker_api {
    server 127.0.0.1:8000 fail_timeout=30s;
}

# HTTP → HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name tracker.yourdomain.com;

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name tracker.yourdomain.com;

    # SSL certificates (will be configured by certbot)
    ssl_certificate /etc/letsencrypt/live/tracker.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tracker.yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Logging
    access_log /var/log/nginx/tracker_access.log;
    error_log /var/log/nginx/tracker_error.log;

    # Client body size limit
    client_max_body_size 1M;

    # Proxy to API
    location /api/ {
        # Rate limiting
        limit_req zone=tracker_limit burst=20 nodelay;

        # Proxy settings
        proxy_pass http://tracker_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API docs
    location /docs {
        proxy_pass http://tracker_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /redoc {
        proxy_pass http://tracker_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /openapi.json {
        proxy_pass http://tracker_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://tracker_api/api/v1/health;
        proxy_set_header Host $host;
    }

    # Block common attack vectors
    location ~ /\. {
        deny all;
    }

    location ~ ^/(config|\.git|\.env) {
        deny all;
    }
}
```

### Enable Nginx Configuration

```bash
# Test configuration
sudo nginx -t

# Create symbolic link
sudo ln -s /etc/nginx/sites-available/tracker /etc/nginx/sites-enabled/

# Reload Nginx
sudo systemctl reload nginx

# Check status
sudo systemctl status nginx
```

---

## SSL/TLS Configuration

### Install Let's Encrypt Certificate

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate (interactive)
sudo certbot --nginx -d tracker.yourdomain.com

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose whether to redirect HTTP to HTTPS (recommended: yes)

# Verify certificate
sudo certbot certificates
```

### Auto-Renewal

Certbot automatically installs a renewal cron job. Verify:

```bash
# Test renewal (dry run)
sudo certbot renew --dry-run

# Check renewal timer
sudo systemctl status certbot.timer

# View renewal logs
sudo journalctl -u certbot.timer
```

### Manual Renewal

If needed, renew manually:

```bash
sudo certbot renew
sudo systemctl reload nginx
```

---

## Security Hardening

### Firewall Configuration

```bash
# Enable UFW
sudo ufw --force enable

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (IMPORTANT: Do this first!)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw reload

# Check status
sudo ufw status verbose
```

### SSH Hardening

Edit `/etc/ssh/sshd_config`:

```bash
# Disable root login
PermitRootLogin no

# Use SSH keys only
PasswordAuthentication no
PubkeyAuthentication yes

# Disable empty passwords
PermitEmptyPasswords no

# Limit users
AllowUsers tracker

# Change default port (optional)
Port 2222  # Remember to update UFW rules
```

Restart SSH:

```bash
sudo systemctl restart sshd
```

### Application Security

**1. Environment Variables**

Never hardcode secrets. Use environment files:

```bash
# /home/tracker/tracker/.env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
JWT_SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:////home/tracker/.config/tracker/tracker.db
```

Load in systemd service:

```ini
[Service]
EnvironmentFile=/home/tracker/tracker/.env
```

**2. File Permissions**

```bash
# Restrict database access
chmod 600 /home/tracker/.config/tracker/tracker.db
chown tracker:tracker /home/tracker/.config/tracker/tracker.db

# Restrict config file
chmod 600 /home/tracker/tracker/.env
chown tracker:tracker /home/tracker/tracker/.env

# Application directory
chmod 755 /home/tracker/tracker
chown -R tracker:tracker /home/tracker/tracker
```

**3. Database Backup Encryption**

```bash
# Encrypted backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/home/tracker/backups"
DB_PATH="/home/tracker/.config/tracker/tracker.db"

# Backup and encrypt
sqlite3 "$DB_PATH" ".backup '/tmp/tracker_backup.db'"
gpg --symmetric --cipher-algo AES256 \
    --output "$BACKUP_DIR/tracker_$DATE.db.gpg" \
    /tmp/tracker_backup.db
rm /tmp/tracker_backup.db

# Upload to remote (optional)
# scp "$BACKUP_DIR/tracker_$DATE.db.gpg" user@backup-server:/backups/
```

**4. Rate Limiting (Application Level)**

Add to `tracker/api/main.py`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to endpoints
@app.get("/api/v1/entries/")
@limiter.limit("100/minute")
async def list_entries(...):
    ...
```

---

## Monitoring & Logging

### Application Logs

```bash
# View all logs
sudo journalctl -u tracker-api

# Follow logs
sudo journalctl -u tracker-api -f

# Last 100 lines
sudo journalctl -u tracker-api -n 100

# Filter by time
sudo journalctl -u tracker-api --since "1 hour ago"
sudo journalctl -u tracker-api --since "2025-10-21 10:00"

# Filter by priority
sudo journalctl -u tracker-api -p err  # Errors only
```

### Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/tracker_access.log

# Error logs
sudo tail -f /var/log/nginx/tracker_error.log

# Filter by status code
grep "500" /var/log/nginx/tracker_access.log

# Count requests by IP
awk '{print $1}' /var/log/nginx/tracker_access.log | sort | uniq -c | sort -nr
```

### Health Checks

Add health check endpoint to `tracker/api/main.py`:

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

app.include_router(router, prefix="/api/v1")
```

Monitor with:

```bash
# Manual check
curl https://tracker.yourdomain.com/health

# Automated monitoring (cron)
*/5 * * * * curl -sf https://tracker.yourdomain.com/health || echo "API down!" | mail -s "Alert" admin@yourdomain.com
```

### External Monitoring

Consider using:

- **UptimeRobot** (free) - HTTP monitoring
- **Healthchecks.io** (free tier) - Cron job monitoring
- **Sentry** - Error tracking
- **Datadog/New Relic** - Full observability (paid)

---

## Backup & Restore

### Automated Backup Script

Create `/home/tracker/backup.sh`:

```bash
#!/bin/bash
set -euo pipefail

# Configuration
BACKUP_DIR="/home/tracker/backups"
DB_PATH="/home/tracker/.config/tracker/tracker.db"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
echo "Starting backup: $DATE"
sqlite3 "$DB_PATH" ".backup '$BACKUP_DIR/tracker_$DATE.db'"

# Compress
gzip "$BACKUP_DIR/tracker_$DATE.db"
echo "Backup completed: tracker_$DATE.db.gz"

# Clean old backups
find "$BACKUP_DIR" -name "tracker_*.db.gz" -mtime +$RETENTION_DAYS -delete
echo "Cleaned backups older than $RETENTION_DAYS days"

# Optional: Upload to remote storage
# aws s3 cp "$BACKUP_DIR/tracker_$DATE.db.gz" s3://your-bucket/backups/
# rclone copy "$BACKUP_DIR/tracker_$DATE.db.gz" remote:backups/
```

Make executable:

```bash
chmod +x /home/tracker/backup.sh
```

### Schedule Backups

Add to crontab:

```bash
# Edit crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /home/tracker/backup.sh >> /home/tracker/backup.log 2>&1

# Hourly backup (if needed)
0 * * * * /home/tracker/backup.sh >> /home/tracker/backup.log 2>&1
```

### Restore from Backup

```bash
# Stop service
sudo systemctl stop tracker-api

# Restore database
gunzip -c /home/tracker/backups/tracker_20251021_020000.db.gz > /tmp/restore.db
mv /home/tracker/.config/tracker/tracker.db /home/tracker/.config/tracker/tracker.db.old
mv /tmp/restore.db /home/tracker/.config/tracker/tracker.db

# Fix permissions
chmod 600 /home/tracker/.config/tracker/tracker.db
chown tracker:tracker /home/tracker/.config/tracker/tracker.db

# Start service
sudo systemctl start tracker-api

# Verify
curl https://tracker.yourdomain.com/health
```

---

## Troubleshooting

### Service Won't Start

**Check logs:**
```bash
sudo journalctl -u tracker-api -n 50
```

**Common issues:**
- Permission denied → Check file ownership
- Port already in use → Check if another process is using port 8000
- Module not found → Reinstall dependencies

**Solution:**
```bash
# Check what's using port 8000
sudo lsof -i :8000

# Reinstall dependencies
cd /home/tracker/tracker
source .venv/bin/activate
uv pip install -e .

# Check permissions
ls -la /home/tracker/.config/tracker/
```

### Nginx 502 Bad Gateway

**Causes:**
- API service not running
- Firewall blocking internal communication
- Socket timeout

**Solution:**
```bash
# Check API status
sudo systemctl status tracker-api

# Test API directly
curl http://127.0.0.1:8000/api/v1/health

# Check Nginx error log
sudo tail -f /var/log/nginx/tracker_error.log

# Restart services
sudo systemctl restart tracker-api
sudo systemctl restart nginx
```

### SSL Certificate Issues

**Certificate not valid:**
```bash
# Check certificate
sudo certbot certificates

# Renew certificate
sudo certbot renew --force-renewal

# Reload Nginx
sudo systemctl reload nginx
```

### High Memory Usage

**Check memory:**
```bash
# Overall system memory
free -h

# Process memory
ps aux | grep tracker

# Check for memory leaks
sudo systemctl restart tracker-api
```

**Solutions:**
- Reduce number of workers in systemd service
- Add swap space
- Upgrade server RAM

### Database Locked

**Symptom:** `database is locked` errors

**Solution:**
```bash
# Stop all services
sudo systemctl stop tracker-api

# Remove lock files
rm /home/tracker/.config/tracker/tracker.db-wal
rm /home/tracker/.config/tracker/tracker.db-shm

# Restart
sudo systemctl start tracker-api
```

---

## Performance Optimization

### Enable Gzip Compression

Add to Nginx configuration:

```nginx
# Inside server block
gzip on;
gzip_vary on;
gzip_types application/json text/plain text/css application/javascript;
gzip_comp_level 6;
```

### Database Optimization

```bash
# Vacuum database
sqlite3 /home/tracker/.config/tracker/tracker.db "VACUUM;"

# Analyze tables
sqlite3 /home/tracker/.config/tracker/tracker.db "ANALYZE;"

# Check database size
du -h /home/tracker/.config/tracker/tracker.db
```

### Increase Worker Processes

Edit systemd service to add more workers:

```ini
ExecStart=/home/tracker/tracker/.venv/bin/uvicorn tracker.api.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --workers 4 \    # Increase from 2
    --log-level info
```

---

## Updating the Application

```bash
# Switch to tracker user
sudo su - tracker

# Navigate to application
cd /home/tracker/tracker

# Pull latest changes
git pull origin main

# Activate virtual environment
source .venv/bin/activate

# Update dependencies
uv pip install -e .

# Run migrations (if any)
# python scripts/migrate.py

# Restart service
sudo systemctl restart tracker-api

# Verify
curl https://tracker.yourdomain.com/health
```

---

## Production Checklist

Before going live, verify:

- [ ] Domain DNS configured
- [ ] SSL certificate installed and valid
- [ ] Firewall configured (ports 22, 80, 443)
- [ ] Systemd service enabled and running
- [ ] Nginx configured and running
- [ ] Application accessible via HTTPS
- [ ] API health check responding
- [ ] Admin user created
- [ ] AI provider configured with production key
- [ ] Backups configured and tested
- [ ] Monitoring configured
- [ ] Security headers present (check with securityheaders.com)
- [ ] Rate limiting configured
- [ ] Logs accessible and rotated
- [ ] SSH hardened (key-only, no root)
- [ ] Database permissions secure (600)

---

**Need Help?** Check the [User Guide](USER_GUIDE.md) or [API Documentation](API_DOCUMENTATION.md).
