#!/bin/bash
# Install and configure Ollama for invoice processing
# Run this script to set up local LLM capabilities

echo "🤖 Installing Ollama for LLM-powered invoice processing..."

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Wait for installation
sleep 5

# Start Ollama service
sudo systemctl start ollama
sudo systemctl enable ollama

# Wait for service to start
sleep 10

# Pull recommended models for invoice processing
echo "📥 Downloading LLM models (this may take a while)..."

# Llama 3.1 8B - Good balance of speed and accuracy
ollama pull llama3.1:8b

# Alternative smaller model for faster processing
ollama pull llama3.1:3b

# Mistral for multilingual support
ollama pull mistral:7b

echo "✅ Ollama installation complete!"
echo ""
echo "Available models:"
ollama list

echo ""
echo "🔧 Configuration:"
echo "- Ollama API endpoint: http://localhost:11434"
echo "- Recommended model for invoices: llama3.1:8b"
echo "- Fast model for testing: llama3.1:3b"
echo ""
echo "🧪 Test the installation:"
echo "curl http://localhost:11434/api/generate -d '{\"model\":\"llama3.1:8b\",\"prompt\":\"Extract invoice data from: FACTUUR V12345 €100.00\",\"stream\":false}'"
echo ""
echo "📝 Next steps:"
echo "1. Update N8N workflow to use n8n-llm-invoice-parser.js"
echo "2. Adjust MODEL_NAME in the parser if needed"
echo "3. Test with real invoice data"
