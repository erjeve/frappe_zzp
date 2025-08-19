# Dutch RGS 3.7 Installation Guide

Complete setup guide for Dutch RGS (Referentie Grootboekschema) 3.7 support in ERPNext using the layered Docker architecture.

## 🎯 Overview

This guide covers:
- Prerequisites and requirements
- Complete installation process
- Verification and testing
- Integration with existing setups
- Troubleshooting common issues

## 📋 Prerequisites

### System Requirements
- Docker Engine 20.10+ with BuildKit support
- Docker Compose v2.0+
- Existing frappe_docker setup (recommended)
- 2GB+ available disk space
- Network access for Docker image pulls

### ERPNext Requirements
- ERPNext v15.0.0 or later
- MariaDB or PostgreSQL database
- Redis for caching and queuing

## 🚀 Installation Steps

### Step 1: Prepare Environment

```bash
# Navigate to your frappe_docker directory
cd /path/to/frappe_docker

# Ensure you have the latest frappe_docker
git pull origin main

# Check current setup (optional)
docker compose ps
```

### Step 2: Build RGS Image

```bash
# Build with default ERPNext version (v15.0.0)
./build-rgs-layered.sh

# Or build with specific version
./build-rgs-layered.sh --erpnext-version v15.1.0

# For multi-platform builds (recommended for production)
./build-rgs-layered.sh --platform linux/amd64,linux/arm64
```

### Step 3: Enable RGS Support

```bash
# Enable RGS in your environment
./enable-rgs-support.sh
```

This script will:
- ✅ Add RGS override to your compose configuration
- ✅ Set Dutch environment variables
- ✅ Configure automatic RGS installation
- ✅ Preserve your existing setup

### Step 4: Deploy with RGS

```bash
# Stop existing services (if running)
docker compose down

# Start with RGS support
docker compose up -d

# Monitor RGS installation
docker compose logs -f rgs-installer
```

### Step 5: Verify Installation

```bash
# Check all services are running
docker compose ps

# Verify RGS installer completed successfully
docker compose logs rgs-installer | grep "✅"

# Check ERPNext is accessible
curl -s http://localhost:8080/api/method/ping
```

## 🔍 Verification

### 1. Check RGS Custom Fields

In ERPNext:
1. Go to **Setup → Customize → Custom Field**
2. Filter by **Document Type = Account**
3. Verify these fields exist:
   - `rgs_code` (RGS Code)
   - `rgs_group` (RGS Group)
   - `rgs_title` (RGS Title)  
   - `rgs_description` (RGS Description)

### 2. Check Dutch Chart of Accounts Template

1. Go to **Accounting → Chart of Accounts**
2. Click **Actions → Chart of Accounts Importer**
3. Verify **"Dutch RGS 3.7 ZZP Template"** is available

### 3. Verify Dutch Localization

```bash
# Check locale in container
docker compose exec backend locale

# Should show: nl_NL.UTF-8
```

## 🔧 Integration with Existing Setups

### With HTTPS/SSL
```bash
# Your existing HTTPS setup remains unchanged
ls overrides/compose.https.yaml  # ✅ Still works

# RGS integrates seamlessly
docker compose \
  -f compose.yaml \
  -f overrides/compose.https.yaml \
  -f overrides/compose.rgs.yaml \
  up -d
```

### With Custom Domains
```bash
# Custom domain setup is preserved
docker compose \
  -f compose.yaml \
  -f overrides/compose.custom-domain.yaml \
  -f overrides/compose.rgs.yaml \
  up -d
```

### With OCR Service
```bash
# OCR and RGS work together
docker compose \
  -f compose.yaml \
  -f overrides/compose.ocr.yaml \
  -f overrides/compose.rgs.yaml \
  up -d
```

## 🏢 ZZP (Freelancer) Setup

For Dutch ZZP businesses:

### 1. Create New Site with RGS Template

```bash
# Create site with Dutch RGS template
docker compose exec backend bench new-site \
  your-site.local \
  --admin-password admin \
  --mariadb-root-password root \
  --install-app erpnext \
  --country Netherlands
```

### 2. Import RGS Chart of Accounts

1. Login to ERPNext as Administrator
2. Go to **Accounting → Chart of Accounts**
3. Click **Actions → Chart of Accounts Importer**
4. Select **"Dutch RGS 3.7 ZZP Template"**
5. Click **Import**

### 3. Configure Company Settings

1. Set **Country = Netherlands**
2. Set **Default Currency = EUR**
3. Configure **Tax Settings** for Dutch VAT (BTW)

## 🐛 Troubleshooting

### RGS Installer Fails to Start

```bash
# Check if ERPNext backend is ready
docker compose logs backend | grep "listening"

# Restart RGS installer if needed
docker compose restart rgs-installer
docker compose logs -f rgs-installer
```

### Custom Fields Not Created

```bash
# Check RGS installer logs
docker compose logs rgs-installer

# Manually run RGS installation
docker compose exec backend python /home/frappe/rgs_scripts/add_complete_rgs.py
```

### Locale Issues

```bash
# Verify Dutch locale is installed
docker compose exec backend locale -a | grep nl_NL

# If missing, rebuild RGS image
./build-rgs-layered.sh --no-cache
```

### Database Connection Issues

```bash
# Check database connectivity
docker compose exec backend bench --site all list-apps

# Verify database service
docker compose ps | grep -E "(mariadb|postgres)"
```

## 🔄 Updates and Maintenance

### Updating ERPNext Version

```bash
# Build with new version
./build-rgs-layered.sh --erpnext-version v15.2.0

# Restart services
docker compose down
docker compose up -d
```

### Updating RGS Components

```bash
# Rebuild RGS image with latest changes
./build-rgs-layered.sh --no-cache

# Restart with new image
docker compose down
docker compose up -d
```

## 📞 Support

### Common Issues
- [Troubleshooting Guide](../docs/troubleshoot.md)
- [Environment Variables](../docs/environment-variables.md)
- [Site Operations](../docs/site-operations.md)

### Community
- [Frappe Discord](https://discord.gg/frappe)
- [ERPNext Forum](https://discuss.erpnext.com/)
- [GitHub Issues](https://github.com/frappe/frappe_docker/issues)

### Netherlands-Specific
- Dutch ERPNext User Group (if available)
- Local ERP consultants familiar with RGS requirements

---

**🇳🇱 Voor Nederlandse ondersteuning, raadpleeg de ERPNext Nederland community**
