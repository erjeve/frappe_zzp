#!/bin/bash

# Test ERPNext private file access
echo "Testing ERPNext private file download..."

# You'll need to replace these with your actual ERPNext API credentials
API_KEY="your_api_key_here"  # Get from ERPNext User Settings
API_SECRET="your_api_secret_here"  # Get from ERPNext User Settings

FILE_URL="/private/files/Abonnementsfactuur V0125079630.pdf"
FULL_URL="https://frappe.fivi.eu${FILE_URL}"

echo "Testing file_url field access patterns..."
echo "1. Direct URL access test..."
echo "URL: $FULL_URL"

# Test with API authentication
curl -I -H "Authorization: token ${API_KEY}:${API_SECRET}" "$FULL_URL" 2>/dev/null || echo "Direct access test - check response above"

echo ""
echo "2. Testing via ERPNext file API..."
API_URL="https://frappe.fivi.eu/api/method/frappe.core.doctype.file.file.download_file?file_url=${FILE_URL}"
echo "API URL: $API_URL"

curl -I -H "Authorization: token ${API_KEY}:${API_SECRET}" "$API_URL" 2>/dev/null || echo "API access test - check response above"

echo ""
echo "3. Check your N8N HTTP Request node:"
echo "   - Current URL template: https://frappe.fivi.eu{{ \$json.file_url }}"
echo "   - Should resolve to: $FULL_URL"
echo "   - Authentication: ERPNext API credentials should be configured"
echo ""
echo "4. If private file access fails, update HTTP Request URL to:"
echo "   https://frappe.fivi.eu/api/method/frappe.core.doctype.file.file.download_file?file_url={{ \$json.file_url }}"
