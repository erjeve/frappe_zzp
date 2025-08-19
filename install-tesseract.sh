#!/bin/bash
# Install Tesseract OCR and Python dependencies for hybrid invoice processing

echo "� Installing Tesseract OCR and dependencies for hybrid processing..."

# Update package list
sudo apt update

# Install Tesseract OCR with language packs
echo "📦 Installing Tesseract OCR..."
sudo apt install -y tesseract-ocr tesseract-ocr-nld tesseract-ocr-eng

# Install image processing libraries
echo "📦 Installing image processing libraries..."
sudo apt install -y poppler-utils libpoppler-dev imagemagick

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install --user \
    pytesseract \
    Pillow \
    pdf2image \
    PyMuPDF \
    requests

# Verify Tesseract installation
echo "✅ Verifying Tesseract installation..."
tesseract --version
echo ""

# Test OCR with simple text
echo "🧪 Testing OCR capabilities..."
echo "Available languages:"
tesseract --list-langs
echo ""

# Make the hybrid processor executable
chmod +x /opt/frappe_docker/hybrid_invoice_processor.py

echo "✅ Installation complete!"
echo ""
echo "📋 Installed components:"
echo "  • Tesseract OCR with Dutch and English language support"
echo "  • PDF to image conversion (poppler-utils, pdf2image)"
echo "  • Python OCR libraries (pytesseract, PIL, PyMuPDF)"
echo ""
echo "🧪 Test the hybrid processor:"
echo "  python3 /opt/frappe_docker/hybrid_invoice_processor.py <pdf_file> <extracted_text> <output.json>"
echo ""
echo "📝 Next steps:"
echo "  1. Update N8N workflow to use hybrid processing"
echo "  2. Test with real invoice PDFs"
echo "  3. Compare accuracy vs text-only extraction"

# Install Python dependencies for OCR processing
pip3 install pytesseract pillow pdf2image opencv-python numpy

echo "✅ Tesseract installation complete!"
echo ""
echo "📦 Installed components:"
echo "- Tesseract OCR engine"
echo "- Dutch (nld) and English (eng) language packs"
echo "- PDF to image conversion tools"
echo "- Python OCR libraries"
echo ""
echo "🧪 Test the installation:"
echo "tesseract --version"
echo ""
echo "📍 OCR with coordinates example:"
echo "tesseract image.png output -c tessedit_create_tsv=1"
echo ""
echo "🔧 Next steps:"
echo "1. Update N8N workflow to use OCR processing"
echo "2. Convert PDF to image before OCR"
echo "3. Extract text with positional coordinates"
echo "4. Use coordinates for accurate field extraction"
