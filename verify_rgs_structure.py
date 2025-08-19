#!/usr/bin/env python3
"""
Verify RGS 3.7 installation by checking custom fields and data structure
"""

import csv
import os

def verify_rgs_csv():
    """Verify the RGS CSV structure and ZZP entries"""
    csv_file = '/opt/frappe_docker/definitief_rgs_3_7.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ RGS CSV file not found: {csv_file}")
        return False
    
    print("🔍 Analyzing Dutch RGS 3.7 CSV structure...")
    
    zzp_count = 0
    level_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Skip the first line (filter info)
            headers = next(reader)  # Get the actual headers
            
            print(f"📋 CSV Headers: {headers[:10]}...")  # Show first 10 headers
            
            # Find key column indices
            ref_code_idx = headers.index('Referentiecode')
            zzp_idx = headers.index('ZZP')
            level_idx = headers.index('Nivo')
            
            for row in reader:
                if len(row) > zzp_idx and row[zzp_idx] == '1':  # ZZP applicable
                    zzp_count += 1
                    level = int(row[level_idx]) if row[level_idx].isdigit() else 0
                    if level in level_counts:
                        level_counts[level] += 1
                        
                    # Show some examples
                    if zzp_count <= 5:
                        print(f"  Example: {row[ref_code_idx]} - Level {level}")
                        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False
    
    print(f"\n📊 RGS Analysis Results:")
    print(f"   Total ZZP-applicable entries: {zzp_count}")
    print(f"   Distribution by level:")
    for level, count in level_counts.items():
        if count > 0:
            print(f"     Level {level}: {count} entries")
    
    return True

if __name__ == "__main__":
    print("🇳🇱 Dutch RGS 3.7 Verification Tool")
    print("===================================")
    verify_rgs_csv()
