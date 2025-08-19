#!/bin/bash

# Test Enhanced Invoice Parser with Real Data
echo "🧪 Testing Enhanced Invoice Parser..."

# Test the enhanced parser with the Dutch invoice data
echo "1. Testing enhanced parser with webhook simulation..."

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
    "creation": "'$(date -Iseconds)'",
    "api_key": "Enter_Your_ERPNext_API_Key_Here",
    "api_secret": "Enter_Your_ERPNext_API_Secret_Here"
  }'

echo -e "\n✅ Webhook sent! Now check the N8N workflow execution:"
echo ""
echo "📊 N8N Workflow URL: https://n8n.fivi.eu/workflow/whH30IauM87zxsZE/executions"
echo ""
echo "🔍 Expected workflow steps:"
echo "   1. Webhook Trigger ✓"
echo "   2. HTTP Request (Download PDF) ✓"
echo "   3. Extract from File (Get text) ✓" 
echo "   4. Code Node (Enhanced Parser) ← NEW!"
echo "   5. Switch Node (Confidence routing) ← NEW!"
echo "   6. Create Purchase Invoice ← UPDATED!"
echo ""
echo "📋 What the enhanced parser will extract:"
echo "   • Supplier: Freedom Internet B.V."
echo "   • Invoice Number: V0125079630"
echo "   • Date: 2025-01-25"
echo "   • Line Items: Internet service, domain registration"
echo "   • Totals: €45.00 incl VAT"
echo "   • VAT: €7.85 (21%)"
echo ""
echo "🎯 Expected confidence scores:"
echo "   • Supplier matching: 80%+ (if exists in ERPNext)"
echo "   • Line item extraction: 70%+"
echo "   • Total amounts: 90%+"
echo "   • Overall confidence: 75-85%"
echo ""
echo "🚦 Routing decision:"
echo "   • >85% confidence → Auto-create Purchase Invoice"
echo "   • 60-85% confidence → Create draft + review notification"
echo "   • <60% confidence → Create basic draft + manual flag"
echo ""
echo "📝 Manual review triggers:"
echo "   • New supplier (Freedom Internet B.V.)"
echo "   • Unmatched line items"
echo "   • Math validation issues"
echo ""
echo "🔧 To update your N8N workflow:"
echo "   1. Replace the Code node content with enhanced parser"
echo "   2. Add Switch node for confidence routing"
echo "   3. Update Purchase Invoice creation with parsed data"
echo ""
echo "📖 Next steps:"
echo "   1. Check execution results in N8N"
echo "   2. Review supplier and item matching"
echo "   3. Verify Purchase Invoice creation"
echo "   4. Test with different invoice types"
