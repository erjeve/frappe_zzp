#!/usr/bin/env python3
"""
Add a custom RGS field to the Account DocType and update existing accounts
"""

import requests
import json
import logging
import csv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_rgs_field_to_account():
    base_url = "https://frappe.fivi.eu"
    
    # API credentials
    api_key = "5aa7a57e4f4645e"
    api_secret = "d22b1d4e85233d8"
    
    headers = {
        "Authorization": f"token {api_key}:{api_secret}",
        "Content-Type": "application/json"
    }
    
    try:
        # Step 1: Create Custom Field for RGS Code
        logger.info("Creating custom RGS field for Account DocType...")
        
        custom_field_data = {
            "doctype": "Custom Field",
            "dt": "Account",
            "label": "RGS Code",
            "fieldname": "rgs_code",
            "fieldtype": "Data",
            "insert_after": "account_number",
            "in_list_view": 1,
            "in_standard_filter": 1,
            "search_index": 1,
            "description": "Official Dutch RGS (Referentie Grootboek Schema) identifier code",
            "length": 20
        }
        
        # Check if field already exists
        existing_field_response = requests.get(
            f"{base_url}/api/resource/Custom Field",
            params={
                "filters": json.dumps([["dt", "=", "Account"], ["fieldname", "=", "rgs_code"]])
            },
            headers=headers
        )
        
        if existing_field_response.status_code == 200:
            existing_fields = existing_field_response.json().get('data', [])
            if existing_fields:
                logger.info("✅ RGS Code field already exists")
                field_exists = True
            else:
                # Create the custom field
                field_response = requests.post(
                    f"{base_url}/api/resource/Custom Field",
                    json=custom_field_data,
                    headers=headers
                )
                
                if field_response.status_code in [200, 201]:
                    logger.info("✅ RGS Code custom field created successfully")
                    field_exists = True
                else:
                    logger.error(f"Failed to create custom field: {field_response.status_code}")
                    logger.error(f"Response: {field_response.text}")
                    field_exists = False
        else:
            logger.error(f"Failed to check existing fields: {existing_field_response.status_code}")
            field_exists = False
        
        if not field_exists:
            return
        
        # Step 2: Load RGS mapping
        logger.info("Loading RGS ID mapping...")
        
        rgs_mapping = {}
        with open('/opt/frappe_docker/dutch_zzp_coa_corrected.csv', 'r') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                rgs_id = row.get('ID', '').strip()
                acc_number = row.get('Account Number', '').strip()
                acc_name = row.get('Account Name', '').strip()
                
                if rgs_id and acc_number:
                    rgs_mapping[acc_number] = rgs_id
        
        logger.info(f"Loaded {len(rgs_mapping)} RGS ID mappings")
        
        # Step 3: Update existing accounts with RGS codes
        logger.info("Updating existing accounts with RGS codes...")
        
        company_name = "Universal Design"
        
        # Get all accounts for the company
        accounts_response = requests.get(
            f"{base_url}/api/resource/Account",
            params={
                "filters": json.dumps([["company", "=", company_name]]),
                "fields": json.dumps(["name", "account_name", "account_number"]),
                "limit_page_length": 1000
            },
            headers=headers
        )
        
        if accounts_response.status_code == 200:
            accounts_data = accounts_response.json()
            accounts = accounts_data.get('data', [])
            
            logger.info(f"Found {len(accounts)} accounts to update")
            
            updated_count = 0
            skipped_count = 0
            
            for acc in accounts:
                acc_name = acc.get('name', '')
                acc_number = acc.get('account_number', '').strip()
                
                if acc_number and acc_number in rgs_mapping:
                    rgs_code = rgs_mapping[acc_number]
                    
                    # Update the account with RGS code
                    update_data = {
                        "rgs_code": rgs_code
                    }
                    
                    update_response = requests.put(
                        f"{base_url}/api/resource/Account/{acc_name}",
                        json=update_data,
                        headers=headers
                    )
                    
                    if update_response.status_code in [200, 201]:
                        logger.info(f"✅ Updated {acc_name}: {acc_number} → {rgs_code}")
                        updated_count += 1
                    else:
                        logger.warning(f"❌ Failed to update {acc_name}: {update_response.status_code}")
                        if updated_count < 5:  # Show first few errors
                            logger.warning(f"    Response: {update_response.text}")
                else:
                    skipped_count += 1
            
            logger.info(f"\n📊 Update Summary:")
            logger.info(f"  ✅ Updated accounts: {updated_count}")
            logger.info(f"  ⏭️  Skipped accounts: {skipped_count}")
            logger.info(f"  📋 Total accounts: {len(accounts)}")
            
            # Step 4: Verify the updates
            logger.info("\n🔍 Verifying RGS code updates...")
            
            # Get sample accounts with RGS codes
            sample_response = requests.get(
                f"{base_url}/api/resource/Account",
                params={
                    "filters": json.dumps([
                        ["company", "=", company_name],
                        ["rgs_code", "!=", ""]
                    ]),
                    "fields": json.dumps(["name", "account_name", "account_number", "rgs_code"]),
                    "limit_page_length": 10
                },
                headers=headers
            )
            
            if sample_response.status_code == 200:
                sample_data = sample_response.json()
                sample_accounts = sample_data.get('data', [])
                
                logger.info(f"Sample accounts with RGS codes:")
                for acc in sample_accounts:
                    acc_name = acc.get('account_name', 'N/A')
                    acc_number = acc.get('account_number', 'N/A')
                    rgs_code = acc.get('rgs_code', 'N/A')
                    logger.info(f"  {rgs_code} | {acc_number} | {acc_name}")
            
            logger.info(f"\n🎉 RGS field implementation complete!")
            logger.info(f"Benefits:")
            logger.info(f"  • Clean account names (no cluttered RGS codes)")
            logger.info(f"  • Searchable RGS codes in filters")
            logger.info(f"  • Sortable by RGS code")
            logger.info(f"  • Reportable RGS compliance")
            logger.info(f"  • Future extensibility for more RGS metadata")
            
        else:
            logger.error(f"Failed to get accounts: {accounts_response.status_code}")
            
    except Exception as e:
        logger.error(f"RGS field addition failed: {e}")

if __name__ == "__main__":
    add_rgs_field_to_account()
