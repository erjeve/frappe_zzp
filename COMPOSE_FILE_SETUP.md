# Docker Compose Environment Setup

## Using COMPOSE_FILE Environment Variable

Instead of using the `compose.sh` script, you can set the `COMPOSE_FILE` environment variable to specify multiple compose files:

### Option 1: Export in shell session
```bash
export COMPOSE_FILE="compose.yaml:overrides/compose.mariadb.yaml:overrides/compose.mariadb-secrets.yaml:overrides/compose.redis.yaml:overrides/compose.https.yaml:overrides/compose.ocr.yaml:docker-compose.volumes.yml"

# Then use standard docker compose commands
docker compose up -d
docker compose down
docker compose ps
```

### Option 2: Add to .env file
Add this line to your `.env` file:
```properties
COMPOSE_FILE=compose.yaml:overrides/compose.mariadb.yaml:overrides/compose.mariadb-secrets.yaml:overrides/compose.redis.yaml:overrides/compose.https.yaml:overrides/compose.ocr.yaml:docker-compose.volumes.yml
```

### Option 3: Create a .env.compose file
```bash
# Create dedicated compose environment file
cat > .env.compose << 'EOF'
COMPOSE_FILE=compose.yaml:overrides/compose.mariadb.yaml:overrides/compose.mariadb-secrets.yaml:overrides/compose.redis.yaml:overrides/compose.https.yaml:overrides/compose.ocr.yaml:docker-compose.volumes.yml
EOF

# Source it when needed
source .env.compose
docker compose up -d
```

## Current Override Files in Use

Based on your `compose.sh` script, you're using:
1. `compose.yaml` - Base Frappe services
2. `overrides/compose.mariadb.yaml` - MariaDB database
3. `overrides/compose.mariadb-secrets.yaml` - Database secrets
4. `overrides/compose.redis.yaml` - Redis cache/queue
5. `overrides/compose.https.yaml` - Traefik HTTPS with Let's Encrypt
6. `overrides/compose.ocr.yaml` - OCR service (newly added)
7. `docker-compose.volumes.yml` - Volume configurations

## Benefits of COMPOSE_FILE approach

- No need to maintain custom scripts
- Standard Docker Compose workflow
- Easy to modify override combinations
- Environment-specific configurations
- Better IDE support for docker compose commands

## OCR Service Status

✅ OCR service successfully deployed and operational:
- Container: `frappe_docker-ocr-service-1`
- Health endpoint: https://ocr.fivi.eu/health
- Ready for N8N integration
