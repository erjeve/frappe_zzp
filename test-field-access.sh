#!/bin/bash

echo "Testing different N8N field access patterns..."

echo "Testing with current JSON webhook format..."

# Test different field access patterns by triggering webhook multiple times
echo "1. Test webhook trigger..."
curl -s -X POST "https://n8n.fivi.eu/webhook/erpnext-file-upload" \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "test-field-access.pdf",
    "file_url": "/private/files/Abonnementsfactuur V0125079630.pdf",
    "file_size": 48684,
    "file_type": "PDF",
    "attached_to_doctype": "Purchase Invoice",
    "attached_to_name": "TEST-FIELD-ACCESS",
    "folder": "Home/Attachments",
    "is_private": 1,
    "owner": "test@example.com",
    "creation": "'$(date -Iseconds)'"
  }' > /dev/null

echo "✓ Webhook triggered"
echo ""
echo "Now try these URL patterns in your N8N HTTP Request node:"
echo ""
echo "1. {{ \$json.file_url }}"
echo "2. {{ \$json.body.file_url }}"
echo "3. {{ \$('Webhook').item.json.body.file_url }}"
echo "4. Hardcoded: /private/files/Abonnementsfactuur V0125079630.pdf"
echo ""
echo "Check N8N execution logs after each change to see which works:"
echo "https://n8n.fivi.eu/workflow/whH30IauM87zxsZE/executions"
