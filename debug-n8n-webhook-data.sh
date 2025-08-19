#!/bin/bash

# Test N8N HTTP Request with hardcoded URL to verify ERPNext API access
echo "Testing N8N HTTP Request with known file URL..."

# Test the exact URL that should work
TEST_URL="/private/files/Abonnementsfactuur%20V0125079630.pdf"

echo "Testing file download API with known URL..."
curl -X POST "https://n8n.fivi.eu/webhook/erpnext-file-upload" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "file_name=Abonnementsfactuur%20V0125079630.pdf&file_url=${TEST_URL}&file_size=48684&file_type=PDF&attached_to_doctype=Purchase%20Invoice&attached_to_name=ACC-PINV-2025-00002&folder=Home/Attachments&is_private=1&owner=ict@fivi.eu&creation=2025-08-04%2023:44:45.216367"

echo ""
echo "Check N8N execution to see:"
echo "1. What data structure the webhook receives"
echo "2. If the debug node shows the file_url correctly"
echo "3. Whether the HTTP Request can access the file_url field"

echo ""
echo "If file_url is still empty, try these N8N HTTP Request URL patterns:"
echo "- {{ \$json.file_url }}"
echo "- {{ \$json.body.file_url }}"
echo "- {{ \$json.query.file_url }}"
echo "- {{ \$json.form.file_url }}"
echo "- {{ \$('Webhook').item.json.file_url }}"
