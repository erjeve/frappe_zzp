#!/usr/bin/env python3
import frappe
import logging

# Initialize site
frappe.init(site='${SITE_NAME}')
frappe.connect()

try:
    logging.info('🇳🇱 Adding Dutch RGS 3.7 custom fields...')
    
    # RGS Referentiecode field
    if not frappe.db.exists('Custom Field', {'dt': 'Account', 'fieldname': 'rgs_code'}):
        rgs_code_field = frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Account',
            'label': 'RGS Referentiecode',
            'fieldname': 'rgs_code',
            'fieldtype': 'Data',
            'description': 'Nederlandse RGS (Referentie Grootboekschema) code voor belastingrapportage volgens versie 3.7',
            'insert_after': 'account_currency'
        })
        rgs_code_field.insert()
        print('✅ RGS Referentiecode field added')
    else:
        print('✅ RGS Referentiecode field already exists')
    
    # RGS Omslagcode field
    if not frappe.db.exists('Custom Field', {'dt': 'Account', 'fieldname': 'rgs_group_code'}):
        rgs_group_field = frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Account',
            'label': 'RGS Omslagcode',
            'fieldname': 'rgs_group_code',
            'fieldtype': 'Data',
            'description': 'RGS omslagcode voor groepering van rekeningen volgens Nederlandse standaard',
            'insert_after': 'rgs_code'
        })
        rgs_group_field.insert()
        print('✅ RGS Omslagcode field added')
    else:
        print('✅ RGS Omslagcode field already exists')
        
    # RGS Referentienummer field
    if not frappe.db.exists('Custom Field', {'dt': 'Account', 'fieldname': 'rgs_reference_number'}):
        rgs_ref_field = frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Account',
            'label': 'RGS Referentienummer',
            'fieldname': 'rgs_reference_number',
            'fieldtype': 'Data',
            'description': 'RGS referentienummer voor unieke identificatie binnen het grootboekschema',
            'insert_after': 'rgs_group_code'
        })
        rgs_ref_field.insert()
        print('✅ RGS Referentienummer field added')
    else:
        print('✅ RGS Referentienummer field already exists')
    
    # RGS Niveau field
    if not frappe.db.exists('Custom Field', {'dt': 'Account', 'fieldname': 'rgs_level'}):
        rgs_level_field = frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Account',
            'label': 'RGS Niveau',
            'fieldname': 'rgs_level',
            'fieldtype': 'Int',
            'description': 'RGS hiërarchie niveau (1=hoofdgroep, 2=groep, 3=subgroep, etc.)',
            'insert_after': 'rgs_reference_number'
        })
        rgs_level_field.insert()
        print('✅ RGS Niveau field added')
    else:
        print('✅ RGS Niveau field already exists')
    
    # Commit changes
    frappe.db.commit()
    
    print('🎉 Dutch RGS 3.7 custom fields installation completed successfully!')
    print('📊 All Account records now have RGS compliance fields')
    print('🇳🇱 ZZP-compliant bookkeeping structure is ready!')
    print('')
    print('Next steps:')
    print('1. Access ERPNext at http://localhost:8080')
    print('2. Create a new Company')
    print('3. Use the standard Chart of Accounts')
    print('4. The RGS fields are now available for all accounts')
    
except Exception as e:
    print(f'❌ RGS installation failed: {e}')
    import traceback
    traceback.print_exc()
finally:
    frappe.destroy()
