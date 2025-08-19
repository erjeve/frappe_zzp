#!/bin/bash

# Disable Dutch RGS 3.7 Support (Profiles Architecture)
# This script disables RGS and cleans up configuration
#
# Features:
# - Removes RGS profile from Docker Compose configuration
# - Cleans up RGS-related compose overrides
# - Preserves existing stack configuration
# - Safe rollback to standard frappe/erpnext setup
#
# IDEMPOTENT: Safe to run multiple times

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚫 Disabling Dutch RGS 3.7 Support (Profiles Architecture)${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo ""

# Configuration files
ENV_FILE=".env"
COMPOSE_FILE="compose.yaml"
RGS_OVERRIDE="overrides/compose.rgs.yaml"

# Check if we're in the right directory
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}❌ Error: compose.yaml not found. Please run this script from your frappe_docker directory.${NC}"
    exit 1
fi

# Function to remove RGS profile
remove_rgs_profile() {
    local env_file="$1"
    
    if [ ! -f "$env_file" ]; then
        echo -e "${YELLOW}⚠ No .env file found - RGS profile not set${NC}"
        return 0
    fi
    
    # Remove rgs from COMPOSE_PROFILES
    if grep -q "^COMPOSE_PROFILES=" "$env_file"; then
        if grep -q "^COMPOSE_PROFILES=.*rgs" "$env_file"; then
            # Remove rgs profile (handle different positions)
            sed -i 's/^COMPOSE_PROFILES=rgs$/COMPOSE_PROFILES=/' "$env_file"
            sed -i 's/^COMPOSE_PROFILES=rgs,/COMPOSE_PROFILES=/' "$env_file"  
            sed -i 's/^COMPOSE_PROFILES=\(.*\),rgs$/COMPOSE_PROFILES=\1/' "$env_file"
            sed -i 's/^COMPOSE_PROFILES=\(.*\),rgs,/COMPOSE_PROFILES=\1,/' "$env_file"
            
            # Remove empty COMPOSE_PROFILES line
            sed -i '/^COMPOSE_PROFILES=$/d' "$env_file"
            
            echo -e "${GREEN}✓ Removed RGS profile from COMPOSE_PROFILES${NC}"
        else
            echo -e "${YELLOW}⚠ RGS profile not found in COMPOSE_PROFILES${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ No COMPOSE_PROFILES found in $env_file${NC}"
    fi
}

# Function to remove compose override
remove_compose_override() {
    local env_file="$1"
    local override_file="$2"
    
    if [ ! -f "$env_file" ]; then
        return 0
    fi
    
    # Remove RGS override from COMPOSE_FILE
    if grep -q "^COMPOSE_FILE=" "$env_file"; then
        if grep -q "$override_file" "$env_file"; then
            # Remove the override file from COMPOSE_FILE
            sed -i "s|:$override_file||g" "$env_file"
            sed -i "s|$override_file:||g" "$env_file"
            sed -i "s|$override_file||g" "$env_file"
            
            # Clean up any resulting empty or malformed COMPOSE_FILE
            sed -i 's/^COMPOSE_FILE=:*/COMPOSE_FILE=/' "$env_file"
            sed -i 's/^COMPOSE_FILE=.*:$/COMPOSE_FILE=compose.yaml/' "$env_file"
            sed -i '/^COMPOSE_FILE=$/d' "$env_file"
            
            echo -e "${GREEN}✓ Removed RGS override from COMPOSE_FILE${NC}"
        else
            echo -e "${YELLOW}⚠ RGS override not found in COMPOSE_FILE${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ No COMPOSE_FILE configuration found${NC}"
    fi
}

# Stop RGS-specific services first
echo -e "${YELLOW}Stopping RGS-specific services...${NC}"
if docker compose ps --services | grep -q "rgs-installer"; then
    docker compose down rgs-installer 2>/dev/null || echo -e "${YELLOW}⚠ RGS installer service not running${NC}"
fi

# Remove RGS profile
echo -e "${YELLOW}Removing RGS profile...${NC}"
remove_rgs_profile "$ENV_FILE"

# Remove compose override
echo -e "${YELLOW}Removing compose override...${NC}"
remove_compose_override "$ENV_FILE" "$RGS_OVERRIDE"

echo -e "${GREEN}🎉 Dutch RGS 3.7 support disabled successfully!${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo -e "${YELLOW}  1. Restart services: ${NC}docker compose down && docker compose up -d"
echo -e "${YELLOW}  2. Clean up RGS images (optional): ${NC}docker image rm frappe/erpnext:rgs-latest frappe/erpnext:rgs-3.7"
echo ""
echo -e "${BLUE}Your ERPNext deployment will now use:${NC}"
echo -e "${GREEN}  ✓ Standard frappe/erpnext image${NC}"
echo -e "${GREEN}  ✓ Default ERPNext configuration${NC}"
echo -e "${GREEN}  ✓ Preserved existing overrides${NC}"
echo ""
echo -e "${BLUE}Note: Existing RGS custom fields in the database are preserved${NC}"
echo -e "${BLUE}Re-enable anytime with: ${NC}./enable-rgs-support.sh"
