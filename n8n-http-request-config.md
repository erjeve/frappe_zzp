# N8N HTTP Request Node Configuration for ERPNext File Download

## HTTP Request Node Settings:
- **Node Name**: Download PDF from ERPNext
- **Method**: GET
- **URL**: https://frappe.fivi.eu{{ $json.file_url }}
- **Authentication**: Generic Credential Type
  - **Name**: Authorization
  - **Value**: token YOUR_API_KEY:YOUR_API_SECRET
- **Response Format**: File
- **Response**: Binary Property Name = "data"

## How to get ERPNext API credentials:
1. Login to ERPNext: https://frappe.fivi.eu
2. Go to: User menu → My Settings → API Access
3. Click "Generate Keys"
4. Copy the API Key and API Secret
5. Format as: token API_KEY:API_SECRET

## Example Authorization header:
Authorization: token 1234567890abcdef:fedcba0987654321

## Workflow sequence:
1. Webhook receives file metadata
2. Filter checks file_size and file_type  
3. HTTP Request downloads actual PDF file
4. Extract from File processes the downloaded PDF
5. Code node parses extracted text
6. HTTP Request creates Purchase Invoice

## Troubleshooting:
- If download fails: Check API credentials
- If extraction fails: Verify PDF file downloaded correctly
- Check N8N execution logs for detailed error messages
