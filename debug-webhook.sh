#!/bin/bash

# Test ERPNext webhook connectivity and data format

echo "=== Testing ERPNext to N8N Webhook Connectivity ==="

# Test 1: Direct webhook test with sample ERPNext data
echo "1. Testing N8N webhook with ERPNext-like data..."
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "https://n8n.fivi.eu/webhook/erpnext-file-upload" \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "sample-invoice.pdf",
    "file_url": "/files/sample-invoice.pdf",
    "file_size": 125000,
    "file_type": "pdf",
    "folder": "Home/Attachments",
    "attached_to_doctype": "Purchase Invoice",
    "attached_to_name": "PI-2025-00001",
    "uploaded_by": "Administrator",
    "creation": "'$(date -Iseconds)'",
    "is_private": 0
  }')

echo "Response: $RESPONSE"
echo ""

# Test 2: Check if webhook is reachable from ERPNext container
echo "2. Testing webhook reachability from ERPNext container..."
docker exec frappe_docker-frontend-1 curl -s -I "https://n8n.fivi.eu/webhook/erpnext-file-upload" || \
docker exec frappe_docker-backend-1 curl -s -I "https://n8n.fivi.eu/webhook/erpnext-file-upload" || \
echo "Could not test from ERPNext container - check container names"

echo ""

# Test 3: Check N8N workflow status
echo "3. Check N8N workflow activation status..."
echo "Visit: https://n8n.fivi.eu/workflow/whH30IauM87zxsZE"
echo "Ensure the workflow toggle is ON (green)"

echo ""

# Test 4: Check ERPNext webhook logs
echo "4. Check ERPNext webhook execution logs..."
echo "In ERPNext, go to: Integrations > Webhook > Invoice File Upload Processor"
echo "Look for execution logs and error messages"

echo ""
echo "=== Next Steps ==="
echo "1. Upload a PDF file in ERPNext"
echo "2. Check N8N executions: https://n8n.fivi.eu/workflow/whH30IauM87zxsZE/executions"
echo "3. Check ERPNext System Console for webhook errors"
