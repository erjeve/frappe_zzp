# Dutch RGS 3.7 Support for ERPNext

This directory contains the layered Docker architecture for Dutch RGS (Referentie Grootboekschema) 3.7 support in ERPNext, providing full compliance with Dutch tax and reporting standards for ZZP (freelancer) companies.

## 🇳🇱 Features

- **Complete RGS 3.7 Implementation**: All 4 required fields (RGS Code, Group, Title, Description)
- **ZZP Chart of Accounts**: Pre-configured template for Dutch freelancers
- **Layered Architecture**: Extends standard frappe/erpnext image with minimal overhead
- **Chainable Entrypoints**: Compatible with other frappe_docker extensions
- **Automatic Installation**: Post-deployment RGS setup with no manual steps
- **Dutch Localization**: Full nl_NL.UTF-8 locale support

## 🏗️ Architecture

### Profiles-Based Integration
```
Standard Services (always available):
├── configurator  ← RGS environment
├── backend       ← RGS environment  
├── frontend      ← Dutch locale
├── scheduler     ← RGS environment
├── queue-short   ← RGS environment
├── queue-long    ← RGS environment
└── websocket     ← Dutch locale

RGS-Specific Services (profile: rgs):
└── rgs-installer ← Post-deployment setup
```

**YAML Anchors for Clean Configuration:**
```yaml
x-rgs-environment: &rgs_environment
  RGS_VERSION: "3.7"
  COUNTRY_CODE: "NL" 
  LANG: "nl_NL.UTF-8"
  TZ: "Europe/Amsterdam"

x-dutch-locale: &dutch_locale
  LANG: "nl_NL.UTF-8"
  TZ: "Europe/Amsterdam"
```

**Benefits:**
- ✅ No environment duplication with YAML anchors
- ✅ Profile-based optional integration
- ✅ No entrypoint conflicts with other extensions  
- ✅ Clean, maintainable configuration
- ✅ Compatible with all existing overrides

## 📁 Files

- **`Containerfile`**: Layered RGS extension Dockerfile
- **`docker-entrypoint-rgs.sh`**: Chainable initialization script
- **`rgs-auto-installer.sh`**: Post-deployment RGS installer
- **`docker-bake.hcl`**: Docker Buildx bake configuration

## 🚀 Quick Start

### 1. Build RGS Image
```bash
# From frappe_docker root directory
./build-rgs-layered.sh
```

### 2. Enable RGS Support (Profiles)
```bash
./enable-rgs-support.sh
```

### 3. Deploy with RGS
```bash
# Deploy with RGS profile automatically enabled
docker compose up -d

# Or explicitly specify profile
docker compose --profile rgs up -d
```

The RGS installer will automatically:
- Wait for ERPNext to be ready
- Install RGS custom fields
- Configure Dutch localization
- Set up ZZP chart of accounts template

## 🔧 Advanced Usage

### Profile Management
```bash
# Enable RGS profile
./enable-rgs-support.sh

# Disable RGS profile  
./disable-rgs-support-profiles.sh

# Manual profile control
docker compose --profile rgs up -d        # With RGS
docker compose up -d                       # Without RGS (if not in .env)
```

### Custom ERPNext Version
```bash
./build-rgs-layered.sh --erpnext-version v15.1.0
```

### Multi-platform Build
```bash
./build-rgs-layered.sh --platform linux/amd64,linux/arm64
```

### Combined Profiles
```bash
# RGS + HTTPS
COMPOSE_PROFILES=rgs docker compose \
  -f compose.yaml \
  -f overrides/compose.https.yaml \
  -f overrides/compose.rgs.yaml \
  up -d

# Or set in .env
echo "COMPOSE_PROFILES=rgs" >> .env
docker compose up -d
```

## 🏷️ Image Tags

- `frappe/erpnext:rgs-3.7` - Stable RGS 3.7 release
- `frappe/erpnext:rgs-latest` - Latest RGS build

## 🔗 Integration

This RGS extension is designed to work with all existing frappe_docker overrides:

- ✅ **HTTPS/SSL**: `compose.https.yaml`
- ✅ **Custom domains**: `compose.custom-domain.yaml`
- ✅ **Database**: `compose.mariadb.yaml`, `compose.postgres.yaml`
- ✅ **Backup**: `compose.backup-cron.yaml`
- ✅ **OCR Service**: `compose.ocr.yaml`
- ✅ **N8N Workflows**: `compose.n8n.yaml`

## 🇳🇱 Dutch Compliance

The RGS implementation provides:

### Chart of Accounts Structure
- **Group 1**: Balance Sheet Assets
- **Group 2**: Balance Sheet Liabilities  
- **Group 3**: Profit & Loss Revenue
- **Group 4**: Profit & Loss Expenses
- **Group 8**: Special Accounts

### Custom Fields Added
- **RGS Code**: Official RGS account code
- **RGS Group**: RGS category (1-4, 8)
- **RGS Title**: Official Dutch account name
- **RGS Description**: Detailed account description

### ZZP Template
Pre-configured chart of accounts specifically for Dutch ZZP (freelancer) businesses, including:
- Revenue accounts for different service types
- Expense categories for business costs
- VAT accounts (BTW) for Dutch tax compliance
- Banking and payment accounts

## 🛠️ Maintenance

### Updating Base Image
When a new ERPNext version is released:

```bash
./build-rgs-layered.sh --erpnext-version v15.x.x
./enable-rgs-support.sh
docker compose up -d
```

### Disable RGS Support
```bash
./disable-rgs-support.sh
```

## 📋 Requirements

- Docker with BuildKit support
- docker-compose v2.0+
- Existing frappe_docker setup

## 🤝 Contributing

See the main frappe_docker [CONTRIBUTING.md](../../CONTRIBUTING.md) for contribution guidelines.

## 📄 License

This RGS extension follows the same license as frappe_docker. See [LICENSE](../../LICENSE).

---

**🇳🇱 Nederlandse ERPNext implementatie voor ZZP bedrijven**
