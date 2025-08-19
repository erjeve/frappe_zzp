#!/usr/bin/env python3
"""
Dutch RGS 3.7 Custom Fields Installer (Clean Version)
For use with bench execute command
"""

import frappe
import json


def install_rgs_fields():
    """Install RGS 3.7 custom fields for the current site"""
    
    # Get current site from frappe context (when run via bench execute)
    site_name = frappe.local.site
    print(f"🇳🇱 Installing Dutch RGS 3.7 Custom Fields")
    print(f"==========================================")
    print(f"Installing RGS fields for site: {site_name}")
    
    # RGS 3.7 custom fields configuration
    rgs_fields = [
        {
            "doctype": "Custom Field",
            "dt": "Account",
            "fieldname": "rgs_referentiecode",
            "label": "RGS Referentiecode",
            "fieldtype": "Data",
            "insert_after": "account_number",
            "description": "Nederlandse RGS 3.7 referentiecode voor rapportage",
            "allow_on_submit": 1,
            "in_list_view": 1,
            "in_standard_filter": 1
        },
        {
            "doctype": "Custom Field", 
            "dt": "Account",
            "fieldname": "rgs_omslagcode",
            "label": "RGS Omslagcode",
            "fieldtype": "Data",
            "insert_after": "rgs_referentiecode",
            "description": "RGS omslagcode voor fiscale rapportage",
            "allow_on_submit": 1
        },
        {
            "doctype": "Custom Field",
            "dt": "Account", 
            "fieldname": "rgs_referentienummer",
            "label": "RGS Referentienummer",
            "fieldtype": "Data",
            "insert_after": "rgs_omslagcode",
            "description": "Uniek RGS referentienummer",
            "allow_on_submit": 1
        },
        {
            "doctype": "Custom Field",
            "dt": "Account",
            "fieldname": "rgs_niveau", 
            "label": "RGS Niveau",
            "fieldtype": "Int",
            "insert_after": "rgs_referentienummer",
            "description": "Hiërarchisch niveau in RGS structuur",
            "allow_on_submit": 1,
            "default": "1"
        }
    ]
    
    try:
        print("📋 Creating RGS custom fields...")
        
        # Install each custom field
        for field_config in rgs_fields:
            fieldname = field_config["fieldname"]
            
            # Check if field already exists
            existing = frappe.db.exists("Custom Field", {
                "dt": "Account",
                "fieldname": fieldname
            })
            
            if existing:
                print(f"   ✓ {fieldname} already exists, skipping")
                continue
                
            # Create the custom field
            custom_field = frappe.get_doc(field_config)
            custom_field.insert()
            print(f"   ✓ Created {fieldname}")
        
        # Commit the changes
        frappe.db.commit()
        
        print("✅ RGS 3.7 custom fields installation completed successfully!")
        print("🎯 Dutch tax compliance fields are now available")
        print("📊 Ready for ZZP financial reporting")
        return True
        
    except Exception as e:
        print(f"❌ Error installing RGS fields: {str(e)}")
        frappe.db.rollback()
        return False


# When run via bench execute, this will be executed
if __name__ == "__main__":
    install_rgs_fields()
