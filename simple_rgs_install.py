#!/usr/bin/env python3
"""
Install Dutch RGS 3.7 custom fields - simplified version
"""

import os
import sys
import json

# Add frappe-bench to path
bench_path = '/home/frappe/frappe-bench'
sys.path.insert(0, bench_path)
os.chdir(bench_path)

# Import frappe
import frappe

def main():
    print("🇳🇱 Dutch RGS 3.7 Custom Fields Installer")
    print("==========================================")
    
    # Get site name from environment or use the only available site
    site_name = os.environ.get('SITE_NAME', 'frappe.fivi.eu')
    
    # Initialize frappe for the site
    frappe.init(site=site_name)
    frappe.connect()
    
    try:
        print(f"Installing RGS custom fields for site: {site_name}")
        
        # Field 1: RGS Referentiecode
        if not frappe.db.exists('Custom Field', {'dt': 'Account', 'fieldname': 'rgs_code'}):
            doc = frappe.get_doc({
                'doctype': 'Custom Field',
                'dt': 'Account',
                'label': 'RGS Referentiecode',
                'fieldname': 'rgs_code',
                'fieldtype': 'Data',
                'description': 'Nederlandse RGS code voor belastingrapportage volgens versie 3.7',
                'insert_after': 'account_currency'
            })
            doc.insert()
            print("✅ RGS Referentiecode field added")
        else:
            print("✅ RGS Referentiecode field already exists")
        
        # Field 2: RGS Omslagcode
        if not frappe.db.exists('Custom Field', {'dt': 'Account', 'fieldname': 'rgs_group_code'}):
            doc = frappe.get_doc({
                'doctype': 'Custom Field',
                'dt': 'Account',
                'label': 'RGS Omslagcode',
                'fieldname': 'rgs_group_code',
                'fieldtype': 'Data',
                'description': 'RGS omslagcode voor groepering van rekeningen',
                'insert_after': 'rgs_code'
            })
            doc.insert()
            print("✅ RGS Omslagcode field added")
        else:
            print("✅ RGS Omslagcode field already exists")
        
        # Field 3: RGS Referentienummer
        if not frappe.db.exists('Custom Field', {'dt': 'Account', 'fieldname': 'rgs_reference_number'}):
            doc = frappe.get_doc({
                'doctype': 'Custom Field',
                'dt': 'Account',
                'label': 'RGS Referentienummer',
                'fieldname': 'rgs_reference_number',
                'fieldtype': 'Data',
                'description': 'RGS referentienummer voor unieke identificatie',
                'insert_after': 'rgs_group_code'
            })
            doc.insert()
            print("✅ RGS Referentienummer field added")
        else:
            print("✅ RGS Referentienummer field already exists")
        
        # Field 4: RGS Niveau
        if not frappe.db.exists('Custom Field', {'dt': 'Account', 'fieldname': 'rgs_level'}):
            doc = frappe.get_doc({
                'doctype': 'Custom Field',
                'dt': 'Account',
                'label': 'RGS Niveau',
                'fieldname': 'rgs_level',
                'fieldtype': 'Int',
                'description': 'RGS hiërarchie niveau (1=hoofdgroep, 2=groep, etc.)',
                'insert_after': 'rgs_reference_number'
            })
            doc.insert()
            print("✅ RGS Niveau field added")
        else:
            print("✅ RGS Niveau field already exists")
        
        # Commit changes
        frappe.db.commit()
        
        print("\n✅ Dutch RGS 3.7 custom fields installation completed!")
        print("📊 RGS fields are now available for all Account records")
        print("🇳🇱 Ready for ZZP-compliant Dutch bookkeeping")
        
        # Show field summary
        print("\n📋 Installed RGS Fields:")
        print("   • RGS Referentiecode - Official RGS reference code")
        print("   • RGS Omslagcode - Grouping/offset code")
        print("   • RGS Referentienummer - Reference number")
        print("   • RGS Niveau - Hierarchy level")
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        frappe.destroy()

if __name__ == "__main__":
    main()
