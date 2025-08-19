# Dutch RGS 3.7 for ERPNext 🇳🇱

Complete implementation of the Dutch RGS (Referentie Grootboekschema) 3.7 for ERPNext with full government compliance support.

## 🎯 Features

- ✅ **Complete RGS 3.7 Compliance** - All 4 official RGS fields implemented
- ✅ **Multiple Legal Entity Support** - ZZP, BV, Stichting, and more
- ✅ **Government Reporting Ready** - IB/VPB, BTW, KvK, CBS compliance
- ✅ **Docker Integration** - Ready-to-use Docker images and compose files
- ✅ **Automated Installation** - Custom fields and templates auto-installed
- ✅ **Dutch Locale Support** - Proper formatting and translations

## 📊 Supported Legal Entity Types

| Entity Type | Description | Account Count | Status |
|-------------|-------------|---------------|---------|
| **ZZP** | Zelfstandige Zonder Personeel | 261 | ✅ Production Ready |
| **Complete RGS** | All RGS 3.7 accounts | 4,963 | ✅ Production Ready |
| **BV** | Besloten Vennootschap | 613 | 🚧 Template Available |
| **Stichting** | Foundation | 19 | 🚧 Template Available |
| **EZ/VOF** | Eenmanszaak/Vennootschap | 2,616 | 🚧 Framework Ready |
| **WoCo** | Woningcorporatie | 2,911 | 🚧 Framework Ready |
| **Coop** | Coöperatie | 38 | 🚧 Framework Ready |

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/frappe/frappe_docker.git
cd frappe_docker

# Start with Dutch RGS support
docker-compose -f docker-compose.rgs.yml up -d

# Access ERPNext at http://localhost:8000
# Default credentials: Administrator / admin
```

### Option 2: Build Custom Image

```bash
# Build the Dutch RGS image
./build-rgs-docker.sh

# Run the custom image
docker run -d --name erpnext-rgs \
  -p 8000:8000 \
  -e FRAPPE_SITE_NAME_HEADER=your-domain.com \
  erpnext-rgs-nl:3.7-latest
```

### Option 3: Manual Installation

```bash
# Install RGS custom fields
python3 add_complete_rgs.py

# Copy chart templates
cp nl_rgs_*.json /path/to/erpnext/chart_templates/

# Verify installation
python3 verify_rgs_complete.py
```

## 📋 Installation Steps

### 1. Setup ERPNext with RGS Support

During ERPNext setup wizard:

1. **Select Country**: Netherlands
2. **Chart of Accounts**: Choose appropriate RGS template:
   - `Netherlands - RGS 3.7 ZZP` for independent professionals (✅ Production ready)
   - `Netherlands - RGS 3.7 Complete` for comprehensive RGS access
   - Additional entity templates available for testing

### 2. Configure Company

```json
{
  "company_name": "Your Company Name",
  "country": "Netherlands",
  "currency": "EUR",
  "fiscal_year_start_date": "2025-01-01",
  "chart_of_accounts": "Netherlands - RGS 3.7 ZZP"
}
```

### 3. Verify RGS Fields

After setup, verify that RGS custom fields are available in Account master:

- ✅ **RGS Referentiecode** - Official RGS reference code
- ✅ **RGS Omslagcode** - Cost allocation code  
- ✅ **RGS Sortering** - Report sorting code
- ✅ **RGS Level** - Hierarchy level (1-5)

## 🏗️ Architecture

### RGS Implementation Components

```
rgs_package/
├── chart_templates/          # ERPNext chart templates
│   ├── nl_rgs_zzp_chart.json
│   ├── nl_rgs_bv_chart.json
│   └── nl_rgs_stichting_chart.json
├── custom_fields/            # RGS field definitions
├── fixtures/                 # Base data and configurations
└── scripts/                  # Installation and verification scripts
    ├── add_complete_rgs.py
    └── verify_rgs_complete.py
```

### Filter Logic

The RGS 3.7 uses a sophisticated filter system:

- **Inclusion Filters (Columns I-N)**: "te kiezen bij aard van entiteit"
  - Basic accounts (3,098)
  - Extended accounts (4,036)
  - Entity-specific accounts (ZZP: 261, BV: 613, etc.)

- **Elimination Filters (Columns O-AC)**: "te vervallen bij geen gebruik"
  - Industry-specific accounts (Construction, Agriculture)
  - Legal form-specific accounts
  - Special purpose accounts

## 📊 Government Compliance

This implementation ensures compliance with:

### Tax Reporting
- **Income Tax (IB)** - Personal income tax for ZZP
- **Corporate Tax (VPB)** - Corporate income tax for BV
- **VAT (BTW)** - Value Added Tax reporting

### Government Reporting
- **Chamber of Commerce (KvK)** - Annual filing requirements
- **Statistics Netherlands (CBS)** - Statistical reporting
- **Dutch Central Bank (DNB)** - Financial sector reporting

### Audit Trail
- Complete transaction traceability
- RGS code mapping for all transactions
- Automated report generation

## 🔧 Development

### Adding New Legal Entity Types

1. **Analyze RGS filters** for the entity type
2. **Create filter configuration** in `legal_entities` dict
3. **Test account filtering** with expected counts
4. **Generate chart template** with proper hierarchy
5. **Validate compliance** with Dutch standards

### Custom Field Extensions

```python
# Example: Adding additional RGS fields
custom_fields = [
    {
        "doctype": "Custom Field",
        "dt": "Account", 
        "fieldname": "rgs_sector_code",
        "label": "RGS Sector Code",
        "fieldtype": "Data"
    }
]
```

## 🐳 Docker Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RGS_VERSION` | RGS version | `3.7` |
| `COUNTRY_CODE` | Country code | `NL` |
| `LANG` | System locale | `nl_NL.UTF-8` |
| `TZ` | Timezone | `Europe/Amsterdam` |

### Volume Mounts

```yaml
volumes:
  - erpnext_data:/home/frappe/frappe-bench/sites
  - erpnext_logs:/home/frappe/frappe-bench/logs
  - ./rgs_package:/home/frappe/rgs_package
```

## 📈 Usage Examples

### Creating a ZZP Company

```python
# Create company with ZZP chart
frappe.get_doc({
    "doctype": "Company",
    "company_name": "MyBusiness ZZP",
    "country": "Netherlands", 
    "default_currency": "EUR",
    "chart_of_accounts": "Netherlands - RGS 3.7 ZZP"
}).insert()
```

### Mapping Transactions to RGS

```python
# All accounts automatically have RGS codes
account = frappe.get_doc("Account", "1000 - Kas")
print(f"RGS Code: {account.rgs_referentiecode}")
print(f"RGS Level: {account.rgs_level}")
```

### Generating Reports

```python
# Generate RGS-compliant trial balance
trial_balance = frappe.get_doc({
    "doctype": "Trial Balance",
    "company": "MyBusiness ZZP",
    "from_date": "2025-01-01",
    "to_date": "2025-12-31",
    "include_rgs_codes": True
})
```

## 🤝 Contributing

We welcome contributions to improve Dutch RGS support:

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/rgs-enhancement`)
3. **Test thoroughly** with Dutch accounting requirements  
4. **Submit pull request** with detailed description

### Testing Checklist

- [ ] Account count matches official RGS totals
- [ ] All 4 RGS fields properly populated
- [ ] Chart hierarchy is correct
- [ ] No duplicate or missing accounts
- [ ] Government reporting compatibility

## 📞 Support

- **GitHub Issues**: Report bugs and feature requests
- **ERPNext Community**: General ERPNext support
- **Dutch Accounting**: Consult with local accounting professionals

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ERPNext Team** - For the excellent ERP platform
- **Dutch Government** - For maintaining the RGS standards
- **Netherlands Accountancy Community** - For requirements and feedback

---

**Built with ❤️ for the Dutch business community**

*Ensuring compliance with Dutch accounting standards since 2025*
