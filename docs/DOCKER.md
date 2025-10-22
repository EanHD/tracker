# Daily Tracker - Docker Documentation

**Version:** 1.0.0  
**Last Updated:** October 21, 2025

---

## Quick Start

### 1. Build and Run with Docker Compose

```bash
# Clone repository
git clone https://github.com/yourusername/tracker.git
cd tracker

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env

# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f tracker-api

# Test API
curl http://localhost:8000/api/v1/health
```

### 2. Build Docker Image Only

```bash
# Build image
docker build -t tracker:latest .

# Run container
docker run -d \
  --name tracker-api \
  -p 8000:8000 \
  -e OPENAI_API_KEY="sk-..." \
  -v tracker-data:/home/tracker/.config/tracker \
  tracker:latest

# View logs
docker logs -f tracker-api
```

---

## Architecture

### Multi-Stage Build

The Dockerfile uses a multi-stage build for optimization:

1. **Builder Stage**: Installs dependencies using `uv` (fast)
2. **Runtime Stage**: Minimal image with only runtime dependencies

**Benefits:**
- Smaller final image (~200MB vs ~1GB)
- Faster builds (cached layers)
- More secure (fewer tools in production)

### Image Layers

```
┌─────────────────────────────┐
│ python:3.12-slim (base)    │ 150 MB
├─────────────────────────────┤
│ sqlite3 runtime deps       │  20 MB
├─────────────────────────────┤
│ Python dependencies (.venv)│  50 MB
├─────────────────────────────┤
│ Application code           │  10 MB
└─────────────────────────────┘
Total: ~230 MB
```

---

## Services

### tracker-api

The main API service running FastAPI with uvicorn.

**Ports:**
- `8000:8000` - API endpoint

**Environment Variables:**
- `AI_PROVIDER` - AI service (openai, anthropic, openrouter, local)
- `OPENAI_API_KEY` - OpenAI API key
- `OPENAI_MODEL` - OpenAI model name
- `JWT_SECRET_KEY` - JWT signing key (change in production!)
- `DATABASE_URL` - SQLite database path

**Volumes:**
- `tracker-data:/home/tracker/.config/tracker` - Persistent database

**Health Check:**
- Interval: 30 seconds
- Timeout: 10 seconds
- Endpoint: `GET /api/v1/health`

### nginx (Optional)

Reverse proxy for SSL termination and load balancing.

**Ports:**
- `80:80` - HTTP (redirects to HTTPS)
- `443:443` - HTTPS

**Configuration:**
- Mount custom nginx.conf for SSL
- SSL certificates in `/etc/nginx/ssl`

---

## Configuration

### Environment Variables

Create `.env` file from template:

```bash
cp .env.example .env
```

**Required:**
```env
# AI Provider
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4

# Security (change this!)
JWT_SECRET_KEY=$(openssl rand -hex 32)
```

**Optional:**
```env
# JWT Configuration
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=90

# Logging
LOG_LEVEL=info

# Database (default is fine)
DATABASE_URL=sqlite:////home/tracker/.config/tracker/tracker.db
```

### Volume Mounts

**Persistent Data:**
```yaml
volumes:
  - tracker-data:/home/tracker/.config/tracker  # Database
  - ./logs:/app/logs                            # Application logs (optional)
```

**Development Mounts:**
```yaml
volumes:
  - .:/app                        # Live code reload
  - /app/.venv                   # Exclude venv
```

---

## Docker Compose Commands

### Service Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Stop and remove volumes (WARNING: deletes data!)
docker-compose down -v
```

### Logs

```bash
# View all logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Specific service
docker-compose logs -f tracker-api

# Last 100 lines
docker-compose logs --tail=100 tracker-api
```

### Scaling

```bash
# Run multiple API instances
docker-compose up -d --scale tracker-api=3

# Note: You'll need a load balancer (nginx) for this
```

### Execute Commands

```bash
# Open shell in container
docker-compose exec tracker-api bash

# Run CLI commands
docker-compose exec tracker-api tracker --help
docker-compose exec tracker-api tracker new

# Initialize database
docker-compose exec tracker-api python scripts/init_db.py

# Create admin user
docker-compose exec tracker-api python -c "
from tracker.core.database import SessionLocal
from tracker.core.auth import get_password_hash
from tracker.core.models import User
from datetime import datetime

db = SessionLocal()
user = User(
    username='admin',
    email='admin@example.com',
    hashed_password=get_password_hash('secure_password'),
    created_at=datetime.utcnow()
)
db.add(user)
db.commit()
print(f'Created user: {user.username}')
"
```

---

## Production Deployment

### 1. Build Production Image

```bash
# Build with version tag
docker build -t tracker:1.0.0 -t tracker:latest .

# Tag for registry
docker tag tracker:1.0.0 your-registry.com/tracker:1.0.0
docker tag tracker:latest your-registry.com/tracker:latest

# Push to registry
docker push your-registry.com/tracker:1.0.0
docker push your-registry.com/tracker:latest
```

### 2. Production docker-compose.yml

```yaml
version: '3.8'

services:
  tracker-api:
    image: your-registry.com/tracker:1.0.0
    restart: always
    ports:
      - "127.0.0.1:8000:8000"  # Bind to localhost only
    environment:
      - AI_PROVIDER=${AI_PROVIDER}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - /opt/tracker/data:/home/tracker/.config/tracker
    networks:
      - tracker-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  tracker-network:
    driver: bridge
```

### 3. Use Docker Secrets (Swarm)

```yaml
services:
  tracker-api:
    image: tracker:1.0.0
    secrets:
      - openai_api_key
      - jwt_secret
    environment:
      - AI_PROVIDER=openai
      - OPENAI_API_KEY_FILE=/run/secrets/openai_api_key
      - JWT_SECRET_KEY_FILE=/run/secrets/jwt_secret

secrets:
  openai_api_key:
    external: true
  jwt_secret:
    external: true
```

Create secrets:
```bash
echo "sk-your-key" | docker secret create openai_api_key -
openssl rand -hex 32 | docker secret create jwt_secret -
```

---

## Backup & Restore

### Backup Database

```bash
# Copy database from container
docker-compose exec tracker-api sqlite3 \
  /home/tracker/.config/tracker/tracker.db \
  ".backup '/tmp/backup.db'"

docker cp tracker-api:/tmp/backup.db ./backup.db

# Compress
gzip backup.db

# Upload to remote
aws s3 cp backup.db.gz s3://your-bucket/backups/
```

### Restore Database

```bash
# Stop service
docker-compose stop tracker-api

# Copy backup to container
docker cp backup.db tracker-api:/tmp/restore.db

# Restore
docker-compose exec tracker-api bash -c "
  mv /home/tracker/.config/tracker/tracker.db \
     /home/tracker/.config/tracker/tracker.db.old
  mv /tmp/restore.db /home/tracker/.config/tracker/tracker.db
  chmod 600 /home/tracker/.config/tracker/tracker.db
"

# Start service
docker-compose start tracker-api
```

### Automated Backup Script

```bash
#!/bin/bash
# backup-docker.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/tracker/backups"

mkdir -p "$BACKUP_DIR"

# Backup database
docker-compose exec -T tracker-api sqlite3 \
  /home/tracker/.config/tracker/tracker.db \
  ".backup '/tmp/backup_$DATE.db'"

docker cp "tracker-api:/tmp/backup_$DATE.db" "$BACKUP_DIR/tracker_$DATE.db"
gzip "$BACKUP_DIR/tracker_$DATE.db"

# Clean old backups (keep 30 days)
find "$BACKUP_DIR" -name "tracker_*.db.gz" -mtime +30 -delete

echo "Backup completed: tracker_$DATE.db.gz"
```

Schedule with cron:
```cron
0 2 * * * /opt/tracker/backup-docker.sh >> /opt/tracker/backup.log 2>&1
```

---

## Monitoring

### Health Checks

```bash
# Check container health
docker-compose ps

# Manual health check
curl http://localhost:8000/api/v1/health

# Container health status
docker inspect tracker-api --format='{{.State.Health.Status}}'
```

### Resource Usage

```bash
# Real-time stats
docker stats tracker-api

# Resource limits in docker-compose.yml
services:
  tracker-api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### Logging

```bash
# View logs
docker-compose logs -f tracker-api

# Export logs
docker-compose logs --no-color > tracker.log

# Log rotation (in docker-compose.yml)
services:
  tracker-api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"
```

---

## Development

### Development docker-compose.override.yml

Create `docker-compose.override.yml` for local development:

```yaml
version: '3.8'

services:
  tracker-api:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      # Mount source code for live reload
      - .:/app
      - /app/.venv  # Exclude venv
    environment:
      - LOG_LEVEL=debug
    command: uvicorn tracker.api.main:app \
      --host 0.0.0.0 \
      --port 8000 \
      --reload \
      --log-level debug
```

### Hot Reload

```bash
# Start with override
docker-compose up -d

# Code changes auto-reload
# Edit files and see changes immediately
```

### Run Tests

```bash
# Run tests in container
docker-compose exec tracker-api pytest

# With coverage
docker-compose exec tracker-api pytest --cov=tracker --cov-report=html

# Copy coverage report
docker cp tracker-api:/app/htmlcov ./htmlcov
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs tracker-api

# Check container status
docker-compose ps

# Inspect container
docker inspect tracker-api

# Common issues:
# - Port already in use: Change port in docker-compose.yml
# - Permission denied: Check volume permissions
# - Missing env vars: Verify .env file
```

### Database Locked

```bash
# Stop container
docker-compose stop tracker-api

# Remove lock files
docker-compose exec tracker-api rm \
  /home/tracker/.config/tracker/tracker.db-wal \
  /home/tracker/.config/tracker/tracker.db-shm

# Start container
docker-compose start tracker-api
```

### Reset Everything

```bash
# Stop and remove containers, networks, volumes
docker-compose down -v

# Remove images
docker rmi tracker:latest

# Rebuild from scratch
docker-compose up -d --build
```

### Access Shell

```bash
# Open bash shell
docker-compose exec tracker-api bash

# Or as root (for debugging)
docker-compose exec -u root tracker-api bash

# Run specific command
docker-compose exec tracker-api tracker stats
```

---

## Security Best Practices

1. **Use specific image versions**
   ```dockerfile
   FROM python:3.12.0-slim  # Instead of :latest
   ```

2. **Run as non-root user**
   ```dockerfile
   USER tracker
   ```

3. **Use secrets for sensitive data**
   - Don't hardcode API keys
   - Use Docker secrets or env vars
   - Never commit .env files

4. **Keep images updated**
   ```bash
   docker pull python:3.12-slim
   docker-compose build --no-cache
   ```

5. **Scan for vulnerabilities**
   ```bash
   docker scan tracker:latest
   ```

6. **Limit resource usage**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1.0'
         memory: 512M
   ```

7. **Use read-only filesystem where possible**
   ```yaml
   services:
     tracker-api:
       read_only: true
       tmpfs:
         - /tmp
   ```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t tracker:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
          docker tag tracker:${{ github.sha }} your-registry.com/tracker:latest
          docker push your-registry.com/tracker:latest
```

See [CI/CD documentation](.github/workflows/README.md) for complete examples.

---

**Need Help?** Check the [User Guide](USER_GUIDE.md), [API Documentation](API_DOCUMENTATION.md), or [Deployment Guide](DEPLOYMENT.md).
