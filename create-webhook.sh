#!/bin/bash

# Script to create ERPNext webhook for file uploads
# Run this script to automatically configure the webhook

ERPNEXT_URL="https://frappe.fivi.eu"
API_KEY="your_api_key_here"
API_SECRET="your_api_secret_here"
N8N_WEBHOOK_URL="https://n8n.fivi.eu/webhook/erpnext-file-upload"

# Create webhook configuration
curl -X POST "${ERPNEXT_URL}/api/resource/Webhook" \
  -H "Authorization: token ${API_KEY}:${API_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_doctype": "File",
    "webhook_docevent": "after_insert",
    "request_url": "'${N8N_WEBHOOK_URL}'",
    "request_structure": "JSON",
    "webhook_headers": [
      {
        "key": "Content-Type",
        "value": "application/json"
      }
    ],
    "webhook_data": [
      {
        "fieldname": "file_name",
        "key": "file_name"
      },
      {
        "fieldname": "file_url", 
        "key": "file_url"
      },
      {
        "fieldname": "file_size",
        "key": "file_size"
      },
      {
        "fieldname": "file_type",
        "key": "file_type"
      },
      {
        "fieldname": "attached_to_doctype",
        "key": "attached_to_doctype"
      },
      {
        "fieldname": "attached_to_name", 
        "key": "attached_to_name"
      }
    ],
    "condition": "doc.file_type == \"PDF\"",
    "enabled": 1
  }'

echo "Webhook created successfully!"
