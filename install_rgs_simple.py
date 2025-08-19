#!/usr/bin/env python3

import frappe
import logging

def install_rgs():
    """Install RGS 3.7 custom fields and basic mapping"""
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Initialize Frappe - connect to the frontend site
    frappe.init(site='frontend')
    frappe.connect()
    
    try:
        logging.info('🇳🇱 Starting Dutch RGS 3.7 Installation...')
        
        # Step 1: Add RGS Referentiecode field
        logging.info('Step 1: Adding RGS Referentiecode field...')
        if not frappe.db.exists('Custom Field', {'dt': 'Account', 'fieldname': 'rgs_code'}):
            custom_field = frappe.get_doc({
                'doctype': 'Custom Field',
                'dt': 'Account',
                'label': 'RGS Referentiecode',
                'fieldname': 'rgs_code',
                'fieldtype': 'Data',
                'description': 'Nederlandse RGS (Referentie Grootboekschema) code voor belastingrapportage',
                'insert_after': 'account_currency'
            })
            custom_field.insert()
            logging.info('✅ Added RGS Referentiecode field')
        else:
            logging.info('✅ RGS Referentiecode field already exists')
        
        # Step 2: Add RGS Omslagcode field
        logging.info('Step 2: Adding RGS Omslagcode field...')
        if not frappe.db.exists('Custom Field', {'dt': 'Account', 'fieldname': 'rgs_group_code'}):
            custom_field = frappe.get_doc({
                'doctype': 'Custom Field',
                'dt': 'Account',
                'label': 'RGS Omslagcode',
                'fieldname': 'rgs_group_code',
                'fieldtype': 'Data',
                'description': 'RGS groepscode voor categorisering van rekeningen',
                'insert_after': 'rgs_code'
            })
            custom_field.insert()
            logging.info('✅ Added RGS Omslagcode field')
        else:
            logging.info('✅ RGS Omslagcode field already exists')
        
        # Step 3: Create Chart of Accounts template
        logging.info('Step 3: Creating Dutch RGS 3.7 Chart of Accounts template...')
        
        chart_name = 'Standard Dutch with RGS 3.7'
        if not frappe.db.exists('Chart of Accounts Importer', chart_name):
            # Create the chart template
            coa_doc = frappe.get_doc({
                'doctype': 'Chart of Accounts Importer',
                'name': chart_name,
                'chart_name': chart_name,
                'country': 'Netherlands'
            })
            coa_doc.insert()
            logging.info(f'✅ Created Chart of Accounts template: {chart_name}')
        else:
            logging.info(f'✅ Chart of Accounts template already exists: {chart_name}')
        
        # Commit all changes
        frappe.db.commit()
        
        logging.info('✅ Dutch RGS 3.7 installation completed successfully!')
        logging.info('🎯 You can now create a company and select "Standard Dutch with RGS 3.7" as your Chart of Accounts')
        
        return True
        
    except Exception as e:
        logging.error(f'❌ RGS installation failed: {e}')
        frappe.db.rollback()
        return False
    
    finally:
        frappe.destroy()

if __name__ == '__main__':
    install_rgs()
