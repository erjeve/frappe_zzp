# N8N Filter Node Update for Real ERPNext Data

## Current Issue:
ERPNext sends file_type as "PDF" (uppercase), but your filter might be checking for "pdf" (lowercase)

## Filter Node Conditions to Update:

### Option 1: Case-insensitive check
```javascript
{{ $json.file_type.toLowerCase() === 'pdf' }}
```

### Option 2: Multiple format check  
```javascript
{{ $json.file_type === 'pdf' || $json.file_type === 'PDF' }}
```

### Option 3: Add to existing file_size condition
In your Filter node, update the conditions:
- Condition 1: doc.file_size is greater than 10000 ✓ (already working)
- Condition 2: Add new condition for file_type
  - Field: `file_type`
  - Operation: `is equal to`
  - Value: `PDF` (uppercase)

## Private File Access Issue:
Since is_private = 1 and file_url starts with "/private/", your HTTP Request node needs:
- Proper ERPNext API authentication ✓ (you have this)
- Access to private files permission

### URL Template Options:

**❌ Current (won't work with Form URL-Encoded):**
```
https://frappe.fivi.eu{{ $json.file_url }}
```

**✅ Correct for Form URL-Encoded data:**
```
https://frappe.fivi.eu{{ $('Webhook').item.json.body.file_url }}
```

**✅ Alternative (if above doesn't work):**
```
https://frappe.fivi.eu{{ $node["Webhook"].json["file_url"] }}
```

**✅ Simplest (if data is in body):**
```
https://frappe.fivi.eu{{ $json.body.file_url }}
```

## Form URL-Encoded Field Access Patterns:

For your Filter node conditions:
- **File size**: `{{ $json.body.file_size }}` instead of `{{ $json.file_size }}`
- **File type**: `{{ $json.body.file_type }}` instead of `{{ $json.file_type }}`

## Debugging Field Access:
Add a "Set" node after Webhook to see the actual data structure:
- Field: `debug_data`
- Value: `{{ JSON.stringify($json) }}`

## Test with Real Data:
```bash
curl -X POST "https://n8n.fivi.eu/webhook/erpnext-file-upload" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "file_name=Abonnementsfactuur V0125079630.pdf&file_url=/private/files/Abonnementsfactuur V0125079630.pdf&file_size=48684&file_type=PDF&attached_to_doctype=Purchase Invoice&attached_to_name=ACC-PINV-2025-00002&folder=Home/Attachments&is_private=1&owner=ict@fivi.eu&creation=2025-08-04 23:44:45.216367"
```
