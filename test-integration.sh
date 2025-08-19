#!/bin/bash

# Test script for ERPNext-N8N integration
echo "Testing ERPNext to N8N file upload integration..."

# Test 1: Direct webhook test with JSON (matching updated ERPNext format)
echo "1. Testing N8N webhook with JSON data..."
curl -X POST "https://n8n.fivi.eu/webhook/erpnext-file-upload" \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "Abonnementsfactuur V0125079630.pdf",
    "file_url": "/private/files/Abonnementsfactuur V0125079630.pdf",
    "file_size": 48684,
    "file_type": "PDF",
    "attached_to_doctype": "Purchase Invoice",
    "attached_to_name": "ACC-PINV-2025-00002",
    "folder": "Home/Attachments",
    "is_private": 1,
    "owner": "ict@fivi.eu",
    "creation": "'$(date -Iseconds)'"
  }'

echo -e "\n\n2. Check N8N executions at: https://n8n.fivi.eu/workflow/whH30IauM87zxsZE/executions"
echo "   Look for:"
echo "   - Webhook trigger success"
echo "   - Filter node passing (file_size > 10000)"
echo "   - HTTP Request downloading file successfully"
echo "   - Extract from File processing the PDF"

echo -e "\n3. Next steps for ERPNext testing:"
echo "   - Go to ERPNext: https://frappe.fivi.eu"
echo "   - Create a new Purchase Invoice"
echo "   - Attach a PDF file"
echo "   - Check N8N workflow executions"

echo -e "\n4. Webhook status check:"
echo "   - ERPNext Webhook: https://frappe.fivi.eu/app/webhook/Invoice%20File%20Upload%20Processor"
echo "   - N8N Workflow: https://n8n.fivi.eu/workflow/whH30IauM87zxsZE"
