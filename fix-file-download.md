# Alternative N8N HTTP Request Configurations for ERPNext Files

## Problem Identified:
HTTP Request downloads HTML page (ERPNext account page) instead of PDF file
This indicates authentication/redirect issues with private file access

## Solution 1: Use ERPNext File Download API
**Update HTTP Request URL to:**
```
https://frappe.fivi.eu/api/method/frappe.core.doctype.file.file.download_file?file_url={{ $json.body.file_url }}
```

## Solution 2: Get File Content via API
**HTTP Request Configuration:**
- **Method**: GET
- **URL**: `https://frappe.fivi.eu/api/resource/File?filters=[["file_url","=","{{ $json.body.file_url }}"]]&fields=["content","file_name","file_type"]`
- **Authentication**: ERPNext API
- **Response Format**: JSON

Then use `{{ $json.data[0].content }}` (base64 decoded) for file content

## Solution 3: Direct File Access with Session
**Add Cookie/Session handling:**
- **URL**: `https://frappe.fivi.eu{{ $json.body.file_url }}`  
- **Headers**: 
  - `Cookie: sid=YOUR_SESSION_ID`
  - `Authorization: token API_KEY:API_SECRET`

## Solution 4: File Content from Webhook
**Modify ERPNext webhook to include file content:**
Add to webhook data:
```
"file_content": "{{ doc.get_content() }}"
```

## Testing:
1. Try Solution 1 first (File Download API)
2. Check N8N execution logs for response
3. Verify PDF content is received instead of HTML
