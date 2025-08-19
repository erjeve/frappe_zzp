# ERPNext Webhook Configuration for N8N Invoice Processing

## Webhook Settings:
- **Webhook Name**: Invoice File Upload Processor
- **Document Type**: File
- **Event**: After Insert
- **Request URL**: https://n8n.fivi.eu/webhook/erpnext-file-upload
- **Request Structure**: JSON
- **Webhook Headers**: 
  - Content-Type: application/json
- **Enable**: ✓ (must be checked)
- **Condition**: doc.file_type == "PDF" (note: uppercase PDF)

## Webhook Data (JSON):
{
  "file_name": "{{ doc.file_name }}",
  "file_url": "{{ doc.file_url }}",
  "file_size": "{{ doc.file_size }}",
  "file_type": "{{ doc.file_type }}",
  "folder": "{{ doc.folder }}",
  "attached_to_doctype": "{{ doc.attached_to_doctype }}",
  "attached_to_name": "{{ doc.attached_to_name }}",
  "uploaded_by": "{{ doc.owner }}",
  "creation": "{{ doc.creation }}",
  "is_private": "{{ doc.is_private }}"
}

## Conditions (Recommended Options):

### Option 1: Only PDF files (Simple)
```
doc.file_type == "pdf"
```

### Option 2: PDF files with invoice-related names
```
doc.file_type == "pdf" and ("invoice" in doc.file_name.lower() or "bill" in doc.file_name.lower())
```

### Option 3: PDF files attached to specific doctypes
```
doc.file_type == "pdf" and doc.attached_to_doctype in ["Purchase Invoice", "Supplier", "Purchase Order"]
```

### Option 4: PDF files larger than 10KB (avoid test files)
```
doc.file_type == "pdf" and doc.file_size > 10000
```

### Option 5: No condition (process all files, filter in N8N)
```
(leave empty - recommended for testing)
```

**Recommendation**: Start with **Option 1** (`doc.file_type == "pdf"`) for now since it's working.

## Security:
- ERPNext and N8N are on same Docker network
- Consider adding API key authentication if needed
