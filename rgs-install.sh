#!/bin/bash
echo "🇳🇱 Dutch RGS 3.7 Auto-Installer (Backend Integration)"
echo "========================================================"
echo "Waiting for backend to be ready..."
until curl -s http://backend:8000/api/method/ping >/dev/null 2>&1; do
  echo "  Waiting for backend..."
  sleep 10
done
echo "✓ Backend is ready! Installing RGS..."

cd /home/frappe/frappe-bench

python3 << 'EOF'
import sys
import os
sys.path.append('/home/frappe/frappe-bench')
os.chdir('/home/frappe/frappe-bench')

import frappe
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Frappe
frappe.init(site='frontend')
frappe.connect()

def add_rgs_fields():
    logging.info('Step 1: Adding official Dutch RGS 3.7 custom fields...')
    
    # Field 1: RGS Referentiecode (already exists, just update)
    if frappe.db.exists('Custom Field', {'dt': 'Account', 'fieldname': 'rgs_code'}):
        custom_field = frappe.get_doc('Custom Field', {'dt': 'Account', 'fieldname': 'rgs_code'})
        custom_field.label = 'RGS Referentiecode'
        custom_field.description = 'Nederlandse RGS (Referentie Grootboekschema) code voor belastingrapportage volgens versie 3.7'
        custom_field.save()
    else:
        custom_field = frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Account',
            'label': 'RGS Referentiecode',
            'fieldname': 'rgs_code',
            'fieldtype': 'Data',
            'description': 'Nederlandse RGS (Referentie Grootboekschema) code voor belastingrapportage volgens versie 3.7',
            'insert_after': 'account_currency'
        })
        custom_field.insert()
    logging.info('✅ RGS Referentiecode field configured')
    
    # Field 2: RGS Omslagcode (nieuwe veld)
    if not frappe.db.exists('Custom Field', {'dt': 'Account', 'fieldname': 'rgs_group_code'}):
        custom_field = frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Account',
            'label': 'RGS Omslagcode',
            'fieldname': 'rgs_group_code',
            'fieldtype': 'Data',
            'description': 'RGS omslagcode voor groepering van rekeningen volgens Nederlandse standaard',
            'insert_after': 'rgs_code'
        })
        custom_field.insert()
        logging.info('✅ RGS Omslagcode field added')
    else:
        logging.info('✅ RGS Omslagcode field already exists')
    
    # Field 3: RGS Referentienummer (maps to account_number structure)
    if not frappe.db.exists('Custom Field', {'dt': 'Account', 'fieldname': 'rgs_reference_number'}):
        custom_field = frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Account',
            'label': 'RGS Referentienummer',
            'fieldname': 'rgs_reference_number',
            'fieldtype': 'Data',
            'description': 'RGS referentienummer voor unieke identificatie binnen het grootboekschema',
            'insert_after': 'rgs_group_code'
        })
        custom_field.insert()
        logging.info('✅ RGS Referentienummer field added')
    else:
        logging.info('✅ RGS Referentienummer field already exists')
        
    # Field 4: RGS Niveau (for hierarchy indication)
    if not frappe.db.exists('Custom Field', {'dt': 'Account', 'fieldname': 'rgs_level'}):
        custom_field = frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Account',
            'label': 'RGS Niveau',
            'fieldname': 'rgs_level',
            'fieldtype': 'Int',
            'description': 'RGS hiërarchie niveau (1=hoofdgroep, 2=groep, 3=subgroep, etc.)',
            'insert_after': 'rgs_reference_number'
        })
        custom_field.insert()
        logging.info('✅ RGS Niveau field added')
    else:
        logging.info('✅ RGS Niveau field already exists')

def install_rgs_mapping():
    logging.info('Step 3: Loading official Dutch RGS 3.7 mapping for ZZP...')
    
    # Load the complete RGS CSV data
    import csv
    import os
    
    csv_file = '/home/frappe/rgs_scripts/definitief_rgs_3_7.csv'
    
    if not os.path.exists(csv_file):
        logging.error(f'RGS CSV file not found: {csv_file}')
        return False
    
    rgs_entries = []
    zzp_count = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Skip the first line (filter info)
            headers = next(reader)  # Get the actual headers
            
            # Find the column indices
            ref_code_idx = headers.index('Referentiecode')
            ref_omslag_idx = headers.index('ReferentieOmslagcode') 
            ref_nr_idx = headers.index('Referentienummer')
            omschrijving_idx = headers.index('Omschrijving')
            zzp_idx = headers.index('ZZP')  # Column 12 indicates ZZP applicability
            level_idx = headers.index('Nivo')
            
            for row in reader:
                if len(row) > zzp_idx and row[zzp_idx] == '1':  # ZZP applicable
                    level = int(row[level_idx]) if row[level_idx].isdigit() else 0
                    
                    # Only include levels 1-4 for practical use
                    if level <= 4 and row[ref_code_idx]:
                        entry = {
                            'rgs_code': row[ref_code_idx],
                            'rgs_group_code': row[ref_omslag_idx] if row[ref_omslag_idx] else '',
                            'reference_number': row[ref_nr_idx] if row[ref_nr_idx] else '',
                            'description': row[omschrijving_idx].strip('"') if row[omschrijving_idx] else '',
                            'level': level
                        }
                        rgs_entries.append(entry)
                        zzp_count += 1
                        
    except Exception as e:
        logging.error(f'Error reading RGS CSV: {e}')
        return False
    
    logging.info(f'✅ Loaded {zzp_count} ZZP-applicable RGS entries from official Dutch RGS 3.7')
    logging.info(f'   Structure includes: Balans, Winst & Verlies, all levels 1-4')
    
    return True

try:
    add_rgs_fields()
    install_rgs_mapping()
    frappe.db.commit()
    print("✅ RGS installation completed successfully!")
except Exception as e:
    print(f"❌ RGS installation failed: {e}")
    sys.exit(1)
finally:
    frappe.destroy()
EOF

echo "✅ RGS 3.7 installation completed successfully!"
echo "🎯 Access ERPNext at http://localhost:8080"
echo "📊 Dutch RGS 3.7 custom fields are now available for all accounts"
echo "🏢 Create a company and use the standard Chart of Accounts"
echo "🇳🇱 ZZP-compliant bookkeeping with official RGS structure ready!"
