# N8N Workflow Update: Enhanced Invoice Parser

## Overview
Update your existing N8N workflow to use the enhanced invoice parser with database matching and confidence-based routing.

## Current Workflow Structure
```
1. Webhook (Trigger)
2. HTTP Request (Download PDF) 
3. Extract from File (Get text)
4. [Code Node] ← REPLACE THIS
```

## New Enhanced Workflow Structure
```
1. Webhook (Trigger)
2. HTTP Request (Download PDF)
3. Extract from File (Get text)
4. Code Node: Enhanced Parser ← NEW
5. Switch Node: Confidence Router ← NEW
   ├─ High Confidence (>85%) → Create Invoice
   ├─ Medium Confidence (60-85%) → Create Draft + Review
   └─ Low Confidence (<60%) → Create Basic Draft + Manual Flag
```

## Step-by-Step Implementation

### Step 1: Update Webhook Node (if needed)
Ensure the webhook passes API credentials:
```json
{
  "file_name": "{{ $json.file_name }}",
  "file_url": "{{ $json.file_url }}",
  "api_key": "YOUR_ERPNEXT_API_KEY",
  "api_secret": "YOUR_ERPNEXT_API_SECRET"
}
```

### Step 2: Replace Code Node Content
1. Go to your Code node (after "Extract from File")
2. Replace the entire content with the enhanced parser code
3. Copy the content from: `/opt/frappe_docker/n8n-enhanced-invoice-parser.js`

### Step 3: Add Switch Node After Code Node
Create a Switch node with these conditions:

#### Branch 1: High Confidence (Auto-approve)
- **Condition**: `{{ $json.confidence_score }} >= 0.85`
- **Route**: Direct to Purchase Invoice creation

#### Branch 2: Medium Confidence (Review needed)
- **Condition**: `{{ $json.confidence_score }} >= 0.60 && {{ $json.confidence_score }} < 0.85`
- **Route**: Create draft + send review notification

#### Branch 3: Low Confidence (Manual processing)
- **Condition**: `{{ $json.confidence_score }} < 0.60`
- **Route**: Create basic draft + manual flag

### Step 4: Update Purchase Invoice Creation

For each branch, create HTTP Request nodes to ERPNext:

#### High Confidence Branch: Direct Creation
```javascript
// HTTP Request to /api/resource/Purchase Invoice
{
  "method": "POST",
  "url": "https://frappe.fivi.eu/api/resource/Purchase Invoice",
  "headers": {
    "Authorization": "token {{ $node['Webhook'].json['body']['api_key'] }}:{{ $node['Webhook'].json['body']['api_secret'] }}",
    "Content-Type": "application/json"
  },
  "body": {
    "doctype": "Purchase Invoice",
    "supplier": "{{ $json.extracted_data.supplier_name }}",
    "bill_no": "{{ $json.extracted_data.invoice_number }}",
    "bill_date": "{{ $json.extracted_data.invoice_date }}",
    "posting_date": "{{ new Date().toISOString().split('T')[0] }}",
    "currency": "EUR",
    "items": "{{ $json.extracted_data.line_items }}",
    "remarks": "Auto-processed with {{ Math.round($json.confidence_score * 100) }}% confidence"
  }
}
```

#### Medium Confidence Branch: Draft + Notification
1. **HTTP Request**: Create draft Purchase Invoice (same as above but add `"docstatus": 0`)
2. **Email Node**: Send review notification with details

#### Low Confidence Branch: Basic Draft + Manual Flag
1. **HTTP Request**: Create minimal draft with generic line item
2. **Email Node**: Send manual processing alert

### Step 5: Add Error Handling
Add an error path from the Code node:
```javascript
// If Code node fails, create fallback
{
  "error_mode": true,
  "raw_text": "{{ $json.raw_text }}",
  "needs_manual_processing": true
}
```

## Testing the Enhanced Parser

### Step 1: Run Test Script
```bash
./test-enhanced-parser.sh
```

### Step 2: Monitor N8N Execution
1. Go to: https://n8n.fivi.eu/workflow/whH30IauM87zxsZE/executions
2. Check the latest execution
3. Verify each node output

### Step 3: Expected Results

#### Code Node Output:
```json
{
  "extracted_data": {
    "supplier_name": "Freedom Internet B.V.",
    "invoice_number": "V0125079630", 
    "invoice_date": "2025-01-25",
    "line_items": [...],
    "totals": {...}
  },
  "database_matches": {
    "suppliers": [...],
    "high_confidence_supplier": null
  },
  "human_review_required": {
    "supplier_creation": true,
    "item_mappings": [...],
    "manual_verification": false
  },
  "confidence_score": 0.75
}
```

#### Switch Node Routing:
- Confidence 75% → Medium Confidence Branch
- Creates draft Purchase Invoice + review notification

### Step 4: Verify ERPNext Integration
1. Check Purchase Invoice creation in ERPNext
2. Verify supplier matching worked
3. Review line item extraction accuracy
4. Confirm VAT calculations

## Troubleshooting

### Common Issues:

#### 1. API Authentication Errors
- Verify API key/secret in webhook data
- Check ERPNext user permissions

#### 2. Supplier Not Found
- Parser creates new supplier suggestion
- Review workflow should handle supplier creation

#### 3. Line Item Extraction Issues
- Check PDF text extraction quality
- Review regex patterns in parser
- Fallback to simple parsing

#### 4. Math Validation Failures
- VAT calculations don't match
- Line items sum ≠ total
- Triggers manual review

### Debug Mode:
Add debug information to Code node output:
```javascript
return [{
  json: {
    ...result,
    debug: {
      raw_text: extractedText,
      layout_sections: parser.sections,
      parsing_attempts: {...}
    }
  }
}];
```

## Performance Optimization

### Parallel Processing:
- Supplier search and item matching run in parallel
- Reduces processing time by ~50%

### Caching:
- Consider caching frequent supplier/item matches
- Reduce ERPNext API calls

### Batch Processing:
- Process multiple invoices in sequence
- Rate limit API calls to avoid ERPNext overload

## Next Steps

1. **Test with different invoice formats**
2. **Fine-tune confidence thresholds**
3. **Add more sophisticated item matching**
4. **Implement user feedback loop**
5. **Monitor processing accuracy over time**

Ready to implement? Start with updating the Code node content!
