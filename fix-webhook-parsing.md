# Fix for ERPNext Webhook Data Parsing Issue

## Problem Identified:
ERPNext sends JSON data as the KEY of a Form URL-Encoded body, not as proper form fields.

Current body structure:
```
"body": {
  "{\"file_name\": \"...\", \"file_url\": \"...\"}": ""
}
```

## Solution 1: Change ERPNext Webhook to JSON (Recommended)

### ERPNext Webhook Settings:
- **Request Structure**: JSON (not Form URL-Encoded)
- **Headers**: Content-Type: application/json

### N8N HTTP Request URL:
```
https://frappe.fivi.eu/api/method/frappe.core.doctype.file.file.download_file?file_url={{ $json.file_url }}
```

## Solution 2: Parse Form Data in N8N

### Add Code Node after Webhook:
```javascript
// Parse JSON from form-encoded body
const bodyKeys = Object.keys($input.all()[0].json.body);
const jsonString = bodyKeys[0];
const parsedData = JSON.parse(jsonString);
return [{ json: parsedData }];
```

### N8N HTTP Request URL (after Code node):
```
https://frappe.fivi.eu/api/method/frappe.core.doctype.file.file.download_file?file_url={{ $json.file_url }}
```

## Solution 3: Direct Access (Current Workaround)
### N8N HTTP Request URL:
```javascript
{{ 
  const bodyKeys = Object.keys($json.body);
  const jsonData = JSON.parse(bodyKeys[0]);
  return `https://frappe.fivi.eu/api/method/frappe.core.doctype.file.file.download_file?file_url=${jsonData.file_url}`;
}}
```

**Recommendation: Use Solution 1 (change ERPNext webhook to JSON) for cleanest implementation.**
