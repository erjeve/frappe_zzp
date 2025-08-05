#!/bin/bash
# Build and deploy OC# Check if service exists in docker-compose.yml
if grep -q "ocr-service" docker-compose.yml; then
    echo "OCR service already exists in docker-compose.yml"
else
    echo "Adding OCR service to docker-compose.yml"
    # Add OCR service to docker-compose.yml
    # This would need the actual docker-compose.yml content
fi

# Deploy the service
docker compose up -d ocr-servicefor invoice processing

echo "🔧 Building OCR Service with latest Tesseract..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build the OCR service
echo "📦 Building OCR Docker image..."
cd /opt/frappe_docker/ocr-service

# Build with progress output
docker build -t frappe-ocr-service:latest . --progress=plain

if [ $? -eq 0 ]; then
    echo "✅ OCR service built successfully!"
else
    echo "❌ Build failed!"
    exit 1
fi

# Test the built image
echo "🧪 Testing OCR service..."
docker run --rm frappe-ocr-service:latest tesseract --version

# Start the service
echo "🚀 Starting OCR service..."
cd /opt/frappe_docker

# Add OCR service to existing docker-compose
if grep -q "ocr-service:" docker-compose.yml; then
    echo "OCR service already in docker-compose.yml"
else
    echo "Adding OCR service to docker-compose.yml"
    cat docker-compose-ocr-addon.yml >> docker-compose.yml
fi

# Start/restart the OCR service
docker-compose up -d ocr-service

echo "✅ OCR service deployment complete!"
echo ""
echo "📋 Service endpoints:"
echo "  • Health check: https://ocr.fivi.eu/health"
echo "  • Process invoice: https://ocr.fivi.eu/process-invoice"
echo "  • Internal access: http://ocr-service:8080"
echo ""
echo "🧪 Test the service:"
echo "  curl https://ocr.fivi.eu/health"
echo ""
echo "📝 Next steps:"
echo "  1. Update N8N workflow to use OCR service"
echo "  2. Replace 'Extract from File' with HTTP Request to OCR service"
echo "  3. Send both PDF file and extracted text for validation"

# Show service status
echo ""
echo "📊 Service status:"
docker compose ps ocr-service
