# Dutch RGS 3.7 for ERPNext

This package provides complete Dutch RGS (Referentie Grootboekschema) 3.7 implementation for ERPNext.

## Features

- ✅ Complete RGS 3.7 compliance
- ✅ All 4 official RGS fields implemented
- ✅ Support for multiple legal entity types
- ✅ Government reporting ready
- ✅ Dutch locale and formatting

## Legal Entity Types Supported

- **ZZP** (Zelfstandige Zonder Personeel) - 261 accounts
- **BV** (Besloten Vennootschap) - 613 accounts  
- **Stichting** (Foundation) - 19 accounts
- **Complete RGS** - All 4,963 accounts

## Quick Start

1. Use the Docker image:
   ```bash
   docker run -d --name erpnext-rgs ghcr.io/frappe/erpnext-rgs-nl:3.7-latest
   ```

2. During ERPNext setup, select a Dutch RGS chart template

3. The RGS custom fields will be automatically available

## Manual Installation

If you want to add RGS to an existing ERPNext installation:

1. Run the RGS field installer:
   ```bash
   python3 scripts/add_complete_rgs.py
   ```

2. Copy chart templates to ERPNext:
   ```bash
   cp chart_templates/nl_rgs_*.json /path/to/erpnext/accounts/chart_of_accounts/verified/
   ```

## Compliance

This implementation meets all Dutch government requirements:
- Income Tax (IB/VPB) declarations
- VAT (BTW) reporting
- Chamber of Commerce reporting  
- Statistical reporting (CBS)

## Support

For issues and questions, please refer to the ERPNext Netherlands community.
