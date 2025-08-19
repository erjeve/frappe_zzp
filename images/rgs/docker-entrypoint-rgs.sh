#!/bin/bash
# Chainable RGS Initialization Script  
# This script performs RGS setup and then chains to the next command
# Designed to be composable with other initialization scripts

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🇳🇱 Initializing Dutch RGS 3.7 support...${NC}"

# Set Dutch timezone if not already set
if [ -z "$TZ" ]; then
    export TZ="Europe/Amsterdam"
    echo -e "${YELLOW}Set timezone to Europe/Amsterdam${NC}"
fi

# Ensure RGS directories exist
mkdir -p /home/frappe/rgs_scripts
echo -e "${GREEN}✓ RGS directories ready${NC}"

# Validate RGS files are present
if [ -f "/home/frappe/rgs_scripts/add_complete_rgs.py" ]; then
    echo -e "${GREEN}✓ RGS installation scripts ready${NC}"
else
    echo -e "${YELLOW}⚠ RGS scripts not found - continuing without RGS${NC}"
fi

if [ -f "/home/frappe/frappe-bench/apps/erpnext/erpnext/accounts/doctype/account/chart_of_accounts/verified/nl_rgs_zzp_chart_of_accounts.json" ]; then
    echo -e "${GREEN}✓ Dutch RGS Chart of Accounts template ready${NC}"
else
    echo -e "${YELLOW}⚠ RGS chart template not found - continuing without template${NC}"
fi

echo -e "${BLUE}Dutch RGS initialization complete${NC}"

# Chain to the next command or original entrypoint
# This allows multiple initialization scripts to be chained together
exec "$@"
