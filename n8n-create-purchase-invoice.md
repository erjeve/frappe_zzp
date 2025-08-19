# N8N HTTP Request Node: Create Purchase Invoice in ERPNext

## HTTP Request Settings:
- **Method**: POST
- **URL**: `https://frappe.fivi.eu/api/resource/Purchase Invoice`
- **Authentication**: ERPNext API (use your existing credential)
- **Headers**: 
  - Content-Type: application/json
- **Body**: `{{ JSON.stringify($json.erpnext_data) }}`
- **Response Format**: JSON

## Alternative API Endpoint (if above doesn't work):
- **URL**: `https://frappe.fivi.eu/api/method/frappe.desk.form.save.savedocs`
- **Body**: 
```json
{
  "action": "Save",
  "doctype": "Purchase Invoice", 
  "doc": "{{ JSON.stringify($json.erpnext_data) }}"
}
```

## Test Response:
Success should return:
```json
{
  "data": {
    "name": "ACC-PINV-2025-00003",
    "docstatus": 0,
    ...
  }
}
```

## Error Handling:
Common issues:
- Supplier not found (create supplier first)
- Item codes not found (use item_name instead)
- Account heads missing (adjust tax account names)
- Missing required fields (company, etc.)
