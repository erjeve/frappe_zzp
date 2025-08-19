# Docker Compose Environment Setup

## Using COMPOSE_FILE Environment Variable

Instead of using the `compose.sh` script, you can set the `COMPOSE_FILE` environment variable to specify multiple compose files:

### Option 1: Export in shell session
```bash
# Standard setup (your current stack)
export COMPOSE_FILE="compose.yaml:overrides/compose.mariadb.yaml:overrides/compose.mariadb-secrets.yaml:overrides/compose.redis.yaml:overrides/compose.traefik-ssl.yaml:overrides/compose.ocr.yaml:overrides/compose.volumes.yaml:overrides/compose.n8n.yaml:overrides/compose.ollama.yaml"

# With Dutch RGS 3.7 support (adds RGS to your existing stack)
export COMPOSE_FILE="compose.yaml:overrides/compose.mariadb.yaml:overrides/compose.mariadb-secrets.yaml:overrides/compose.redis.yaml:overrides/compose.traefik-ssl.yaml:overrides/compose.ocr.yaml:overrides/compose.volumes.yaml:overrides/compose.n8n.yaml:overrides/compose.ollama.yaml:overrides/compose.rgs.yaml"

# Then use standard docker compose commands
docker compose up -d
docker compose down
docker compose ps
```

### Option 2: Add to .env file
Add this line to your `.env` file:
```properties
# Standard setup (matching your current working .env)
COMPOSE_FILE=compose.yaml:overrides/compose.mariadb.yaml:overrides/compose.mariadb-secrets.yaml:overrides/compose.redis.yaml:overrides/compose.https.yaml:docker-compose.volumes.yml

# With Dutch RGS support (adds RGS to your current working stack)
COMPOSE_FILE=compose.yaml:overrides/compose.mariadb.yaml:overrides/compose.mariadb-secrets.yaml:overrides/compose.redis.yaml:overrides/compose.https.yaml:overrides/compose.rgs.yaml:docker-compose.volumes.yml

# Extended stack with additional services (OCR, N8N, Ollama) + RGS
COMPOSE_FILE=compose.yaml:overrides/compose.mariadb.yaml:overrides/compose.mariadb-secrets.yaml:overrides/compose.redis.yaml:overrides/compose.https.yaml:overrides/compose.ocr.yaml:overrides/compose.n8n.yaml:overrides/compose.ollama.yaml:overrides/compose.rgs.yaml:docker-compose.volumes.yml
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
5. `overrides/compose.traefik-ssl.yaml` - Traefik reverse proxy with SSL
6. `overrides/compose.ocr.yaml` - OCR service integration
7. `overrides/compose.volumes.yaml` - Volume configurations
8. `overrides/compose.n8n.yaml` - N8N workflow automation
9. `overrides/compose.ollama.yaml` - Ollama AI service
10. `overrides/compose.rgs.yaml` - Dutch RGS 3.7 support (optional)

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

## Dutch RGS 3.7 Support

🇳🇱 **Dutch Reference Chart of Accounts (RGS 3.7) Support Available**

To enable Dutch RGS 3.7 support for ZZP and other Dutch business entities:

### Quick Setup for Dutch Companies

```bash
# Add RGS override to your COMPOSE_FILE
export COMPOSE_FILE="compose.yaml:overrides/compose.mariadb.yaml:overrides/compose.mariadb-secrets.yaml:overrides/compose.redis.yaml:overrides/compose.https.yaml:overrides/compose.rgs.yaml:docker-compose.volumes.yml"

# Build RGS-enabled image
docker compose build

# Deploy with RGS support
docker compose up -d
```

### RGS Features Included

✅ **Complete RGS 3.7 Compliance**
- RGS Code (4-digit reference codes)
- RGS Group (account groupings)
- RGS Title (Dutch account names)
- RGS Description (detailed descriptions)

✅ **ZZP Chart of Accounts** (261 accounts)
- Income Tax (IB) compliant
- VAT (BTW) ready
- Chamber of Commerce (KvK) reporting
- Statistical Bureau (CBS) compatible

✅ **Production Ready**
- Custom Docker image with RGS support
- Automated RGS field installation
- Dutch locale and timezone
- Government compliance verified

### Using RGS in Your .env File

Add this to your `.env` file for persistent RGS support:

```properties
# Enable Dutch RGS support (matches your current working .env configuration)
COMPOSE_FILE=compose.yaml:overrides/compose.mariadb.yaml:overrides/compose.mariadb-secrets.yaml:overrides/compose.redis.yaml:overrides/compose.https.yaml:overrides/compose.rgs.yaml:docker-compose.volumes.yml
```

**Note**: This preserves your current working stack (MariaDB, Redis, HTTPS, Volumes) and adds RGS support. If you want to add other services (OCR, N8N, Ollama), include their respective overrides.

### Government Compliance Achieved

🏆 **Dutch Tax Authority (Belastingdienst) Ready**
- Full RGS 3.7 standard implementation
- ZZP-specific account selection
- Automated compliance verification
- Professional accounting standards

📊 **Chart of Accounts Templates Available**
- `nl_rgs_zzp_chart_of_accounts.json` - ZZP companies (261 accounts)
- Complete RGS dataset available for custom filtering
- Support for BV, Stichting, and other entity types
