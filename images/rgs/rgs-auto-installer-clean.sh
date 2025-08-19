#!/bin/bash
set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if ERPNext backend is ready
wait_for_backend() {
    echo -e "${BLUE}🇳🇱 Dutch RGS 3.7 Auto-Installer (Layered Architecture)${NC}"
    echo -e "${BLUE}==========================================================${NC}"
    
    # Wait for ERPNext backend to be ready
    echo -e "${YELLOW}Waiting for ERPNext backend to be ready...${NC}"
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://backend:8000/api/method/ping >/dev/null 2>&1; then
            echo -e "${GREEN}✓ ERPNext backend is responding!${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}  Attempt $((attempt + 1))/$max_attempts - waiting for backend...${NC}"
        sleep 10
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ ERPNext backend failed to start within 5 minutes${NC}"
    exit 1
}

# Function to install RGS
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
    echo -e "${BLUE}Starting Dutch RGS 3.7 installation...${NC}"
    
    # Wait for backend to be ready
    wait_for_backend
    
    # Install RGS
    if install_rgs; then
        echo -e "${GREEN}✅ RGS installation completed successfully!${NC}"
        echo -e "${BLUE}📊 Dutch Chart of Accounts with RGS 3.7 compliance is now available${NC}"
        
        # Show final instructions
        echo -e "${YELLOW}🎯 Next Steps:${NC}"
        echo -e "  1. Access ERPNext at http://localhost:8080"
        echo -e "  2. Create a new Company"
        echo -e "  3. Select 'Standard Dutch with RGS 3.7' as Chart of Accounts"
        echo -e "  4. Your ZZP administration will be fully RGS 3.7 compliant!"
        echo ""
        echo -e "${GREEN}🇳🇱 Veel succes met je Nederlandse boekhouding!${NC}"
        
    else
        echo -e "${RED}❌ RGS installation failed${NC}"
        echo -e "${YELLOW}💡 You can manually run the RGS installation later:${NC}"
        echo -e "   docker compose exec backend python /home/frappe/rgs_scripts/add_complete_rgs.py"
        exit 1
    fi
}

# Run main function
main "$@"
