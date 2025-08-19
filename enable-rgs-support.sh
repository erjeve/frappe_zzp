#!/bin/bash

# Enable Dutch RGS 3.7 Support (Profiles Architecture)
# This script enables RGS using Docker Compose profiles
# 
# Features:
# - Uses Docker Compose profiles for clean optional integration
# - YAML anchors eliminate environment duplication
# - No entrypoint conflicts with other extensions
# - Automatic post-deployment RGS installation
# - Full Dutch localization support
#
# Idempotent - safe to run multiple times

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🇳🇱 Enabling Dutch RGS 3.7 Support (Profiles Architecture)${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Configuration files
ENV_FILE=".env"
COMPOSE_FILE="compose.yaml"
RGS_OVERRIDE="overrides/compose.rgs.yaml"
RGS_CONTAINERFILE="images/rgs/Containerfile"

# Check if we're in the right directory
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}❌ Error: compose.yaml not found. Run this script from the frappe_docker directory.${NC}"
    exit 1
fi

# Check if RGS Containerfile exists
if [ ! -f "$RGS_CONTAINERFILE" ]; then
    echo -e "${RED}❌ Error: RGS Containerfile not found at $RGS_CONTAINERFILE${NC}"
    echo -e "${YELLOW}Please ensure the layered RGS architecture is properly set up.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Found RGS layered Containerfile${NC}"

# Function to add or update profile in .env
add_rgs_profile() {
    local env_file="$1"
    
    # Create .env if it doesn't exist
    if [ ! -f "$env_file" ]; then
        touch "$env_file"
        echo -e "${YELLOW}Created $env_file${NC}"
    fi
    
    # Check if COMPOSE_PROFILES already exists
    if grep -q "^COMPOSE_PROFILES=" "$env_file"; then
        # Check if rgs profile is already included
        if grep -q "^COMPOSE_PROFILES=.*rgs" "$env_file"; then
            echo -e "${GREEN}✓ RGS profile already enabled in $env_file${NC}"
        else
            # Add rgs to existing profiles
            sed -i 's/^COMPOSE_PROFILES=\(.*\)/COMPOSE_PROFILES=\1,rgs/' "$env_file"
            echo -e "${GREEN}✓ Added RGS profile to existing COMPOSE_PROFILES${NC}"
        fi
    else
        # Add new COMPOSE_PROFILES line
        echo "COMPOSE_PROFILES=rgs" >> "$env_file"
        echo -e "${GREEN}✓ Added COMPOSE_PROFILES=rgs to $env_file${NC}"
    fi
}

# Function to add compose override
add_compose_override() {
    local env_file="$1"
    local override_file="$2"
    
    # Check if COMPOSE_FILE already exists and includes our override
    if grep -q "^COMPOSE_FILE=" "$env_file"; then
        if grep -q "$override_file" "$env_file"; then
            echo -e "${GREEN}✓ RGS override already included in COMPOSE_FILE${NC}"
        else
            # Add our override to existing COMPOSE_FILE
            sed -i "s|^COMPOSE_FILE=\(.*\)|COMPOSE_FILE=\1:$override_file|" "$env_file"
            echo -e "${GREEN}✓ Added $override_file to COMPOSE_FILE${NC}"
        fi
    else
        # Add new COMPOSE_FILE line
        echo "COMPOSE_FILE=compose.yaml:$override_file" >> "$env_file"
        echo -e "${GREEN}✓ Added COMPOSE_FILE with RGS override${NC}"
    fi
}

# Enable RGS profile
echo -e "${YELLOW}Enabling RGS profile...${NC}"
add_rgs_profile "$ENV_FILE"

# Add compose override
echo -e "${YELLOW}Adding compose override...${NC}"
add_compose_override "$ENV_FILE" "$RGS_OVERRIDE"

echo -e "${GREEN}🎉 Dutch RGS 3.7 support enabled successfully!${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo -e "${YELLOW}  1. Build RGS image: ${NC}./build-rgs-layered.sh"
echo -e "${YELLOW}  2. Deploy with RGS: ${NC}docker compose up -d"
echo -e "${YELLOW}  3. Monitor installation: ${NC}docker compose logs -f rgs-installer"
echo ""
echo -e "${BLUE}The RGS installer will automatically:${NC}"
echo -e "${GREEN}  ✓ Install Dutch RGS 3.7 custom fields${NC}"
echo -e "${GREEN}  ✓ Configure Dutch localization${NC}"
echo -e "${GREEN}  ✓ Set up ZZP chart of accounts template${NC}"
echo ""
echo -e "${BLUE}Profile-based architecture benefits:${NC}"
echo -e "${GREEN}  ✓ Clean integration with existing overrides${NC}"
echo -e "${GREEN}  ✓ No entrypoint conflicts${NC}"
echo -e "${GREEN}  ✓ Easy to enable/disable${NC}"
echo -e "${GREEN}  ✓ Maintainable YAML anchors${NC}"
