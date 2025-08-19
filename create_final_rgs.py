#!/usr/bin/env python3
"""
Final Corrected Dutch RGS 3.7 Implementation
============================================

Based on the proper understanding of RGS 3.7 filter logic:

STAGE 1 - SELECT BASE SCHEME (Columns I-M):
- Basis (8): Basic chart - start here for most entities
- Uitgebreid (9): Extended chart - more comprehensive 
- EZ/VOF (10): Sole proprietorship/Partnership specific
- ZZP (11): Independent professional specific
- WoCo (12): Housing corporation specific

STAGE 2 - EXCLUDE IRRELEVANT SECTIONS (Columns N+):
- Inactief (13): Inactive accounts - always exclude
- BB (14): Construction industry - exclude if not construction
- Agro (15): Agriculture - exclude if not agricultural  
- WKR (16): Work cost regulation - exclude if not applicable
- EZ/VOF (17): Additional EZ/VOF - exclude if not EZ/VOF
- BV (18): Private company - exclude if not BV
- WoCo (19): Additional WoCo - exclude if not WoCo
- Bank (20): Banking - exclude if not banking
- Stichting (25): Foundation - exclude if not foundation
- Coop (28): Cooperative - exclude if not cooperative
etc.

CORRECT LOGIC:
1. Start with a base scheme (Basis or Uitgebreid usually)
2. Add entity-specific inclusions if applicable
3. Remove (exclude) sections that don't apply to your entity
"""

import csv
import json
import requests
from typing import Dict, List, Set, Optional
import sys

# ERPNext API Configuration
API_BASE = "https://frappe.fivi.eu/api/resource"
API_KEY = "5aa7a57e4f4645e"
API_SECRET = "d22b1d4e85233d8"

class FinalRGSImplementation:
    def __init__(self):
        self.headers = {
            'Authorization': f'token {API_KEY}:{API_SECRET}',
            'Content-Type': 'application/json'
        }
        
        # Base scheme selection (Stage 1)
        self.base_schemes = {
            'Basis': 8,
            'Uitgebreid': 9,
            'EZ_VOF_base': 10,
            'ZZP_base': 11,
            'WoCo_base': 12
        }
        
        # Exclusion filters (Stage 2) - accounts to REMOVE
        self.exclusion_filters = {
            'Inactief': 13,         # Always exclude
            'BB': 14,               # Construction industry
            'Agro': 15,             # Agriculture
            'WKR': 16,              # Work cost regulation
            'EZ_VOF_extra': 17,     # Additional EZ/VOF
            'BV': 18,               # Private company specific
            'WoCo_extra': 19,       # Additional WoCo
            'Bank': 20,             # Banking specific
            'OZW_Coop_Sticht_FWO': 21,  # Insurance/Coop/Foundation/Research
            'Afrek_syst': 22,       # Deduction system
            'Nivo5': 23,            # Level 5 detail
            'Uitbr5': 24,           # Extended level 5
            'Stichting': 25,        # Foundation specific
            'OZW': 26,              # Insurance specific  
            'FWO': 27,              # Research fund specific
            'Coop': 28              # Cooperative specific
        }
        
        # Entity configurations using correct two-stage logic
        self.legal_entities = {
            'ZZP': {
                'name': 'ZZP (Zelfstandige Zonder Personeel)',
                'description': 'Independent professionals without employees',
                'base_schemes': ['Basis', 'ZZP_base'],  # Start with Basis + ZZP specific
                'exclude_filters': [                    # Exclude everything except ZZP
                    'Inactief', 'BB', 'Agro', 'WKR', 'EZ_VOF_extra', 'BV', 
                    'WoCo_extra', 'Bank', 'Stichting', 'OZW', 'FWO', 'Coop'
                ],
                'expected_count': 261,
                'template_name': 'Netherlands - RGS 3.7 ZZP'
            },
            'BV': {
                'name': 'BV (Besloten Vennootschap)',
                'description': 'Private limited companies',
                'base_schemes': ['Basis', 'Uitgebreid'],  # Start with extended scheme
                'exclude_filters': [                      # Exclude non-BV sections, but keep BV
                    'Inactief', 'EZ_VOF_extra', 'WoCo_extra', 'Stichting', 
                    'OZW', 'FWO', 'Coop'
                    # Note: Don't exclude BV, BB, Agro, WKR, Bank as BV may need these
                ],
                'expected_count': 613,  # BV-specific accounts
                'template_name': 'Netherlands - RGS 3.7 BV'
            },
            'Stichting': {
                'name': 'Stichting (Foundation)',
                'description': 'Foundations and non-profit organizations',
                'base_schemes': ['Basis'],                # Start with basic scheme
                'exclude_filters': [                      # Exclude most, keep only foundation
                    'Inactief', 'BB', 'Agro', 'WKR', 'EZ_VOF_extra', 'BV',
                    'WoCo_extra', 'Bank', 'OZW', 'FWO', 'Coop'
                    # Note: Don't exclude Stichting
                ],
                'expected_count': 19,  # Foundation-specific accounts only
                'template_name': 'Netherlands - RGS 3.7 Stichting'
            },
            'EZ_VOF': {
                'name': 'EZ/VOF (Eenmanszaak/Vennootschap onder Firma)',
                'description': 'Sole proprietorships and partnerships',
                'base_schemes': ['Basis', 'EZ_VOF_base'],  # Basic + EZ/VOF specific
                'exclude_filters': [                       # Keep EZ/VOF, exclude others
                    'Inactief', 'BV', 'WoCo_extra', 'Bank', 'Stichting',
                    'OZW', 'FWO', 'Coop'
                    # Note: May keep BB, Agro, WKR, EZ_VOF_extra for flexibility
                ],
                'expected_count': 2422 + 194,  # Base + additional
                'template_name': 'Netherlands - RGS 3.7 EZ/VOF'
            },
            'WoCo': {
                'name': 'WoCo (Woningcorporatie)',
                'description': 'Housing corporations',
                'base_schemes': ['Basis', 'WoCo_base'],    # Basic + WoCo specific
                'exclude_filters': [                       # Keep WoCo, exclude others
                    'Inactief', 'Agro', 'EZ_VOF_extra', 'BV', 'Bank',
                    'Stichting', 'OZW', 'FWO', 'Coop'
                    # Note: May keep BB, WKR, WoCo_extra for housing sector
                ],
                'expected_count': 2055 + 856,  # Base + additional
                'template_name': 'Netherlands - RGS 3.7 WoCo'
            },
            'Basis_Only': {
                'name': 'Basis (Basic Chart Only)',
                'description': 'Basic chart without entity-specific additions',
                'base_schemes': ['Basis'],                 # Only basic scheme
                'exclude_filters': [                       # Exclude all additions
                    'Inactief', 'BB', 'Agro', 'WKR', 'EZ_VOF_extra', 'BV',
                    'WoCo_extra', 'Bank', 'Stichting', 'OZW', 'FWO', 'Coop'
                ],
                'expected_count': 3098,  # Pure basic scheme
                'template_name': 'Netherlands - RGS 3.7 Basis'
            }
        }

    def load_rgs_data(self) -> List[Dict]:
        """Load and parse the complete RGS 3.7 CSV file"""
        print("Loading complete RGS 3.7 data...")
        
        with open('definitief_rgs_3_7.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        headers = rows[1]
        data_rows = rows[2:-1]  # Exclude headers and totals
        
        accounts = []
        for row in data_rows:
            if len(row) >= len(headers) and row[0]:
                account = {}
                for i, header in enumerate(headers):
                    account[header] = row[i] if i < len(row) else ''
                accounts.append(account)
        
        print(f"Loaded {len(accounts)} RGS accounts")
        return accounts

    def filter_accounts_correct_logic(self, accounts: List[Dict], entity_type: str) -> List[Dict]:
        """Apply correct two-stage RGS filtering logic"""
        if entity_type not in self.legal_entities:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        entity_config = self.legal_entities[entity_type]
        filtered_accounts = []
        
        print(f"Filtering for {entity_type}:")
        print(f"  Stage 1 - Base schemes: {entity_config['base_schemes']}")
        print(f"  Stage 2 - Excluding: {entity_config['exclude_filters']}")
        
        for account in accounts:
            values = list(account.values())
            
            # Stage 1: Check if account is included in any base scheme
            included_in_base = False
            for scheme_name in entity_config['base_schemes']:
                if scheme_name in self.base_schemes:
                    col_idx = self.base_schemes[scheme_name]
                    if len(values) > col_idx and values[col_idx].strip() == '1':
                        included_in_base = True
                        break
            
            if not included_in_base:
                continue  # Account not in any of our base schemes
            
            # Stage 2: Check if account should be excluded
            should_exclude = False
            for exclude_name in entity_config['exclude_filters']:
                if exclude_name in self.exclusion_filters:
                    col_idx = self.exclusion_filters[exclude_name]
                    if len(values) > col_idx and values[col_idx].strip() == '1':
                        should_exclude = True
                        break
            
            if not should_exclude:
                filtered_accounts.append(account)
        
        actual_count = len(filtered_accounts)
        expected_count = entity_config['expected_count']
        
        print(f"  Result: {actual_count} accounts (expected: {expected_count})")
        
        if actual_count != expected_count:
            print(f"  ⚠ Count difference: {actual_count - expected_count}")
            self.analyze_difference(accounts, entity_config, actual_count, expected_count)
        
        return filtered_accounts

    def analyze_difference(self, accounts: List[Dict], entity_config: Dict, actual: int, expected: int):
        """Analyze why the count doesn't match expected"""
        print(f"  📊 Analyzing count difference...")
        
        # Count by base scheme
        for scheme_name in entity_config['base_schemes']:
            if scheme_name in self.base_schemes:
                col_idx = self.base_schemes[scheme_name]
                count = sum(1 for acc in accounts 
                          if len(list(acc.values())) > col_idx and 
                          list(acc.values())[col_idx].strip() == '1')
                print(f"    {scheme_name}: {count} accounts")
        
        # Count by exclusion (what we're removing)
        for exclude_name in entity_config['exclude_filters']:
            if exclude_name in self.exclusion_filters:
                col_idx = self.exclusion_filters[exclude_name]
                count = sum(1 for acc in accounts 
                          if len(list(acc.values())) > col_idx and 
                          list(acc.values())[col_idx].strip() == '1')
                print(f"    Excluding {exclude_name}: {count} accounts")

    def create_template(self, accounts: List[Dict], entity_type: str) -> Dict:
        """Create ERPNext template from filtered accounts"""
        entity_config = self.legal_entities[entity_type]
        
        template = {
            "name": entity_config['template_name'],
            "country_code": "NL",
            "tree": {},
            "description": f"Dutch RGS 3.7 for {entity_config['description']}. Generated using correct two-stage filtering logic.",
            "version": "3.7",
            "legal_entity": entity_type,
            "account_count": len(accounts),
            "rgs_logic": {
                "base_schemes": entity_config['base_schemes'],
                "exclusion_filters": entity_config['exclude_filters'],
                "stage_1": "Include accounts from base schemes",
                "stage_2": "Exclude accounts marked with exclusion filters"
            }
        }
        
        # Build hierarchy
        template["tree"] = self.build_hierarchy(accounts)
        return template

    def build_hierarchy(self, accounts: List[Dict]) -> Dict:
        """Build account hierarchy structure"""
        tree = {
            "BALANS": {
                "account_name": "BALANS",
                "is_group": 1,
                "children": {
                    "ACTIVA": {"account_name": "ACTIVA", "root_type": "Asset", "is_group": 1, "children": {}},
                    "PASSIVA": {"account_name": "PASSIVA", "root_type": "Liability", "is_group": 1, "children": {}},
                    "EIGEN VERMOGEN": {"account_name": "EIGEN VERMOGEN", "root_type": "Equity", "is_group": 1, "children": {}}
                }
            },
            "WINST- EN VERLIESREKENING": {
                "account_name": "WINST- EN VERLIESREKENING",
                "is_group": 1,
                "children": {
                    "OPBRENGSTEN": {"account_name": "OPBRENGSTEN", "root_type": "Income", "is_group": 1, "children": {}},
                    "KOSTEN": {"account_name": "KOSTEN", "root_type": "Expense", "is_group": 1, "children": {}}
                }
            }
        }
        
        # Add accounts to appropriate categories
        for account in accounts:
            rgs_code = account['Referentiecode']
            account_name = account['Omschrijving']
            level = int(account.get('Nivo', '1'))
            
            # Determine category
            if rgs_code.startswith('B'):
                if account.get('D/C') == 'D':
                    category = ["BALANS", "ACTIVA"]
                    root_type = "Asset"
                else:
                    category = ["BALANS", "PASSIVA"]
                    root_type = "Liability"
            elif rgs_code.startswith('W'):
                category = ["BALANS", "EIGEN VERMOGEN"]
                root_type = "Equity"
            elif rgs_code.startswith('O'):
                category = ["WINST- EN VERLIESREKENING", "OPBRENGSTEN"]
                root_type = "Income"
            elif rgs_code.startswith('K'):
                category = ["WINST- EN VERLIESREKENING", "KOSTEN"]
                root_type = "Expense"
            else:
                continue
            
            # Create account entry
            account_entry = {
                "account_name": account_name,
                "account_number": account.get('Referentienummer', ''),
                "root_type": root_type,
                "is_group": 1 if level <= 3 else 0,
                "rgs_referentiecode": rgs_code,
                "rgs_omslagcode": account.get('ReferentieOmslagcode', ''),
                "rgs_sortering": account.get('Sortering', ''),
                "rgs_level": level
            }
            
            # Add to tree
            current = tree
            for cat in category:
                current = current[cat]["children"]
            current[account_name] = account_entry
        
        return tree

    def create_all_corrected_templates(self):
        """Create all templates using corrected logic"""
        accounts = self.load_rgs_data()
        
        print(f"\n{'='*70}")
        print("Creating RGS 3.7 Templates with CORRECTED Two-Stage Logic")
        print(f"{'='*70}")
        
        templates_created = []
        
        for entity_type in self.legal_entities.keys():
            print(f"\n--- {entity_type} ---")
            
            filtered_accounts = self.filter_accounts_correct_logic(accounts, entity_type)
            
            if filtered_accounts:
                template = self.create_template(filtered_accounts, entity_type)
                
                filename = f"nl_rgs_3.7_{entity_type.lower()}_final.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(template, f, indent=2, ensure_ascii=False)
                
                templates_created.append({
                    'entity': entity_type,
                    'filename': filename,
                    'account_count': len(filtered_accounts),
                    'expected_count': self.legal_entities[entity_type]['expected_count'],
                    'status': '✅' if len(filtered_accounts) == self.legal_entities[entity_type]['expected_count'] else '⚠'
                })
                
                print(f"  ✓ Template saved: {filename}")
        
        # Summary
        print(f"\n{'='*70}")
        print("✅ CORRECTED RGS 3.7 Templates Created!")
        print(f"{'='*70}")
        
        for template in templates_created:
            print(f"  {template['status']} {template['entity']:12}: {template['account_count']:4d}/{template['expected_count']:4d} accounts - {template['filename']}")
        
        return templates_created

def main():
    rgs = FinalRGSImplementation()
    rgs.create_all_corrected_templates()

if __name__ == "__main__":
    main()
