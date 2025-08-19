#!/bin/bash

# Disable Dutch RGS 3.7 Support (Layered Architecture)
# This script disables RGS and cleans up configuration
#
# Features:
# - Removes RGS override from compose configuration
# - Cleans up RGS-related environment variables
# - Preserves existing stack configuration
# - Safe rollback to standard frappe/erpnext setup
#
# IDEMPOTENT: Safe to run multiple times

set -e

echo "🚫 Dutch RGS 3.7 Support Disabler"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "compose.yaml" ]; then
    echo "❌ Error: compose.yaml not found. Please run this script from your frappe_docker directory."
    exit 1
fi

# Check if RGS is currently enabled
if [ -f ".env" ] && grep -q "overrides/compose.rgs.yaml" .env 2>/dev/null; then
    echo "📝 RGS support is currently enabled, removing..."
    
    # Backup existing .env
    echo "📋 Backing up existing .env to .env.backup.$(date +%Y%m%d_%H%M%S)"
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    
    # Remove RGS configuration
    echo "🧹 Removing RGS configuration..."
    sed -i '/# Dutch RGS 3.7 Support Configuration/,/^$/d' .env 2>/dev/null || true
    sed -i '/^COMPOSE_FILE=.*compose.rgs.yaml/d' .env 2>/dev/null || true
    
    # Add back standard COMPOSE_FILE without RGS
    cat >> .env << 'EOF'

# Standard Compose Configuration (RGS removed)
COMPOSE_FILE=compose.yaml:overrides/compose.mariadb.yaml:overrides/compose.mariadb-secrets.yaml:overrides/compose.redis.yaml:overrides/compose.https.yaml:docker-compose.volumes.yml
EOF
    
    echo "✅ Dutch RGS 3.7 support disabled!"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Run: docker compose down"
    echo "   2. Run: docker compose up -d"
    echo ""
    echo "⚠️  Note: RGS data in existing companies will remain"
    echo "   To remove RGS fields, run the cleanup script manually"
    
else
    echo "ℹ️  RGS support is not currently enabled in .env"
    echo "   Nothing to disable."
fi

echo ""
echo "🔍 Verifying configuration..."
if docker compose config --quiet 2>/dev/null; then
    echo "✅ Docker Compose configuration is valid"
else
    echo "⚠️  Warning: Docker Compose configuration may have issues"
fi

echo ""
echo "ℹ️  Note: This script is idempotent - safe to run multiple times"
echo "🇳🇱 RGS support management complete! ✨"
