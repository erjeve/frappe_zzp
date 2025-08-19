#!/bin/bash

# Build Dutch RGS 3.7 Docker Image (Layered Architecture)
# This script builds the RGS extension layer using the new layered architecture
# Compatible with frappe_docker patterns and upstream updates
#
# Usage Examples:
#   ./build-rgs-layered.sh                                    # Default build
#   ./build-rgs-layered.sh --erpnext-version v15.1.0         # Specific version
#   ./build-rgs-layered.sh --platform linux/amd64,linux/arm64 # Multi-platform
#   ./build-rgs-layered.sh --push                            # Build and push

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🇳🇱 Building Dutch RGS 3.7 Docker Image (Layered)${NC}"
echo -e "${BLUE}=================================================${NC}"

# Default values
ERPNEXT_VERSION="${ERPNEXT_VERSION:-v15.0.0}"
RGS_VERSION="3.7"
PLATFORM="${PLATFORM:-linux/amd64}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --erpnext-version)
            ERPNEXT_VERSION="$2"
            shift 2
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --push)
            PUSH_IMAGE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --erpnext-version VERSION  ERPNext version to extend (default: v15.0.0)"
            echo "  --platform PLATFORM       Target platform (default: linux/amd64)"
            echo "  --push                     Push image to registry after build"
            echo "  --help                     Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Verify we're in the right directory
if [ ! -f "images/rgs/Containerfile" ]; then
    echo -e "${RED}❌ Error: RGS Containerfile not found${NC}"
    echo -e "${YELLOW}Please run this script from the frappe_docker root directory${NC}"
    exit 1
fi

echo -e "${YELLOW}Building RGS image with:${NC}"
echo -e "${YELLOW}  Base ERPNext version: ${ERPNEXT_VERSION}${NC}"
echo -e "${YELLOW}  RGS version: ${RGS_VERSION}${NC}"
echo -e "${YELLOW}  Platform: ${PLATFORM}${NC}"

# Build the image
echo -e "${BLUE}Starting Docker build...${NC}"

docker build \
    --platform="$PLATFORM" \
    --build-arg ERPNEXT_VERSION="$ERPNEXT_VERSION" \
    --tag "frappe/erpnext:rgs-${RGS_VERSION}" \
    --tag "frappe/erpnext:rgs-latest" \
    --file images/rgs/Containerfile \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
    echo -e "${GREEN}Tags created:${NC}"
    echo -e "${GREEN}  - frappe/erpnext:rgs-${RGS_VERSION}${NC}"
    echo -e "${GREEN}  - frappe/erpnext:rgs-latest${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

# Optional push to registry
if [ "$PUSH_IMAGE" = true ]; then
    echo -e "${BLUE}Pushing images to registry...${NC}"
    docker push "frappe/erpnext:rgs-${RGS_VERSION}"
    docker push "frappe/erpnext:rgs-latest"
    echo -e "${GREEN}✅ Images pushed successfully!${NC}"
fi

echo -e "${BLUE}Build complete! 🇳🇱${NC}"
echo -e "${YELLOW}To use this image, enable RGS support with: ./enable-rgs-support.sh${NC}"
