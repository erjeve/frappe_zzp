#!/bin/bash

# Test ERPNext file download directly
echo "Testing ERPNext file download..."

# First, let's see what a typical ERPNext file URL looks like
echo "1. Testing ERPNext file access..."

# Test with a known ERPNext file path (adjust as needed)
TEST_FILE_URL="https://frappe.fivi.eu/files/sample.pdf"

echo "2. Testing file download from ERPNext..."
curl -I "$TEST_FILE_URL" 2>/dev/null || echo "File URL test failed - this is normal if no test file exists"

echo ""
echo "3. To verify your HTTP Request node:"
echo "   - Upload a PDF in ERPNext"
echo "   - Check the file_url in the webhook payload"
echo "   - Verify the HTTP Request node can download it"
echo "   - Check N8N execution logs for download success/failure"

echo ""
echo "4. Expected file_url formats from ERPNext:"
echo "   - /files/filename.pdf"
echo "   - /private/files/filename.pdf" 
echo "   - /assets/frappe/files/filename.pdf"

echo ""
echo "5. Your current HTTP Request URL template:"
echo "   https://frappe.fivi.eu{{ \$json.file_url }}"
echo "   This should work for most ERPNext file URLs"
