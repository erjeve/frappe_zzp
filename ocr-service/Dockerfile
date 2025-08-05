# Use latest Ubuntu LTS as base - much more reliable than old tesseract images
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies including latest Tesseract
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    tesseract-ocr \
    tesseract-ocr-nld \
    tesseract-ocr-eng \
    poppler-utils \
    libpoppler-dev \
    imagemagick \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Install Python dependencies
COPY requirements-ocr.txt .
RUN pip3 install --no-cache-dir -r requirements-ocr.txt

# Copy the application files
COPY invoice_ocr_api.py .

# Create necessary directories
RUN mkdir -p /app/temp /app/output

# Test Tesseract installation
RUN tesseract --version && tesseract --list-langs

# Expose port for API
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the OCR API server with Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "invoice_ocr_api:app"]
