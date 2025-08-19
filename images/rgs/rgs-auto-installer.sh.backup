#!/bin/bash

# RGS Auto-installer Service for Layered Architecture
# This script runs as a separate service after ERPNext is fully started
# Compatible with the new layered Containerfile approach

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🇳🇱 Dutch RGS 3.7 Auto-Installer (Layered Architecture)${NC}"
echo -e "${BLUE}==========================================================${NC}"

# Wait for ERPNext to be fully ready
wait_for_erpnext() {
    echo -e "${YELLOW}Waiting for ERPNext backend to be ready...${NC}"
    
    local max_attempts=60  # 5 minutes
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        # Check if backend service is responding
        if curl -s http://backend:8000/api/method/ping >/dev/null 2>&1; then
            echo -e "${GREEN}✓ ERPNext backend is responding!${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}  Attempt $((attempt + 1))/$max_attempts - waiting for backend...${NC}"
        sleep 5
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ ERPNext backend failed to start within 5 minutes${NC}"
    return 1
}

# Install RGS custom fields using the layered architecture
install_rgs() {
    echo -e "${YELLOW}Installing RGS 3.7 custom fields (layered architecture)...${NC}"
    
    # Since we're now running as a separate service, we can execute locally
    if python /home/frappe/rgs_scripts/add_complete_rgs.py; then
        echo -e "${GREEN}✓ RGS custom fields installed successfully${NC}"
        return 0
    else
        echo -e "${RED}❌ RGS installation failed${NC}"
        return 1
    fi
}

# Verify RGS installation
verify_rgs() {
    echo -e "${YELLOW}Verifying RGS installation...${NC}"
    
    if docker compose exec -T backend python /home/frappe/rgs_scripts/verify_rgs_complete.py; then
        echo -e "${GREEN}✓ RGS verification passed${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ RGS verification incomplete${NC}"
        return 1
    fi
}

# Main installation process
main() {
    echo -e "${BLUE}Starting automated RGS installation...${NC}"
    
    # Check if RGS is already installed
    if [ -f ".rgs_auto_installed" ]; then
        echo -e "${GREEN}✓ RGS already installed automatically${NC}"
        echo -e "${BLUE}To reinstall, delete .rgs_auto_installed and run again${NC}"
        exit 0
    fi
    
    # Wait for ERPNext to be ready
    if ! wait_for_erpnext; then
        echo -e "${RED}❌ Cannot proceed - ERPNext not ready${NC}"
        exit 1
    fi
    
    # Install RGS components
    echo -e "${BLUE}Installing RGS components...${NC}"
    if install_rgs; then
        echo -e "${GREEN}✓ RGS installation completed${NC}"
        
        # Verify installation
        if verify_rgs; then
            # Mark as automatically installed
            touch .rgs_auto_installed
            
            echo ""
            echo -e "${GREEN}🎉 Dutch RGS 3.7 Auto-Installation Complete!${NC}"
            echo -e "${GREEN}==========================================${NC}"
            echo ""
            echo -e "${GREEN}✓ RGS custom fields installed${NC}"
            echo -e "${GREEN}✓ Chart templates available${NC}"
            echo -e "${GREEN}✓ Ready for Dutch companies${NC}"
            echo ""
            echo -e "${BLUE}📋 Available chart templates:${NC}"
            echo -e "  • Dutch ZZP RGS 3.7 (261 accounts)"
            echo -e "  • Additional RGS templates available"
            echo ""
            echo -e "${BLUE}🚀 Next steps:${NC}"
            echo -e "  1. Access ERPNext: http://your-domain"
            echo -e "  2. Create new company"
            echo -e "  3. Select 'Dutch ZZP RGS 3.7' chart template"
            echo -e "  4. Enjoy compliant Dutch accounting!"
            echo ""
            echo -e "${GREEN}🇳🇱 Nederlandse boekhouding is klaar! ✨${NC}"
        else
            echo -e "${YELLOW}⚠ Installation completed but verification had issues${NC}"
        fi
    else
        echo -e "${RED}❌ RGS installation failed${NC}"
        exit 1
    fi
}

# Handle command line arguments
case "${1:-install}" in
    install)
        main
        ;;
    verify)
        verify_rgs
        ;;
    force)
        rm -f .rgs_auto_installed
        main
        ;;
    *)
        echo -e "${BLUE}Usage: $0 [install|verify|force]${NC}"
        echo -e "  install - Install RGS if not already done (default)"
        echo -e "  verify  - Verify existing RGS installation"
        echo -e "  force   - Force reinstall RGS"
        exit 1
        ;;
esac
