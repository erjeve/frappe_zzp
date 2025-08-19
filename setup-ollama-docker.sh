#!/bin/bash
# Docker-based Ollama setup with model initialization

echo "🤖 Setting up Ollama in Docker with LLM models..."

# Update Docker Compose configuration to include Ollama
if ! grep -q "compose.ollama.yaml" .env; then
    echo "📝 Adding Ollama to Docker Compose configuration..."
    sed -i 's/COMPOSE_FILE=.*/&:overrides\/compose.ollama.yaml/' .env
fi

# Start Ollama service (using official pre-built image)
echo "🐳 Starting Ollama Docker service..."
docker compose up -d ollama

# Wait for Ollama service to be ready
echo "⏳ Waiting for Ollama service to start..."
timeout=120
counter=0
while ! docker compose exec ollama curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        echo "❌ Timeout waiting for Ollama service"
        exit 1
    fi
    sleep 2
    counter=$((counter + 2))
    echo -n "."
done
echo ""

# Pull recommended models for invoice processing
echo "📥 Downloading LLM models (this may take a while)..."

# Check available memory
AVAILABLE_MEM=$(free -g | awk '/^Mem:/{print $7}')
echo "Available system memory: ${AVAILABLE_MEM}GB"

if [ "$AVAILABLE_MEM" -lt 3 ]; then
    echo "⚠️  Limited memory detected. Installing only compact models..."
    echo "Pulling llama3.2:1b (ultra-compact model for limited memory)..."
    docker compose exec ollama ollama pull llama3.2:1b
    RECOMMENDED_MODEL="llama3.2:1b"
elif [ "$AVAILABLE_MEM" -lt 5 ]; then
    echo "Pulling llama3.1:3b (compact model for moderate memory)..."
    docker compose exec ollama ollama pull llama3.1:3b
    RECOMMENDED_MODEL="llama3.1:3b"
else
    echo "Pulling llama3.1:8b (recommended for accuracy)..."
    docker compose exec ollama ollama pull llama3.1:8b
    
    echo "Pulling llama3.1:3b (faster for testing)..."
    docker compose exec ollama ollama pull llama3.1:3b
    
    echo "Pulling mistral:7b (multilingual support)..."
    docker compose exec ollama ollama pull mistral:7b
    RECOMMENDED_MODEL="llama3.1:8b"
fi

echo "✅ Ollama Docker setup complete!"
echo ""
echo "Available models:"
docker compose exec ollama ollama list

echo ""
echo "🔧 Configuration:"
echo "- Ollama API endpoint (internal): http://ollama:11434"
echo "- Ollama API endpoint (external): https://ollama.fivi.eu"
echo "- Recommended model for this system: $RECOMMENDED_MODEL"
echo "- Available models listed above"
echo ""
echo "🧪 Test the installation:"
echo "curl https://ollama.fivi.eu/api/generate -d '{\"model\":\"$RECOMMENDED_MODEL\",\"prompt\":\"Extract invoice data from: FACTUUR V12345 €100.00\",\"stream\":false}'"
echo ""
echo "📝 Next steps:"
echo "1. Create context-aware invoice parser with ERPNext integration"
echo "2. Update N8N workflow to use hybrid OCR + LLM approach"
echo "3. Test with real invoice data and ERPNext context"
