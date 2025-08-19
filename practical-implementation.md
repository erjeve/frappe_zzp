# N8N Enhanced Parser: Practical Implementation Guide

## Using Existing N8N Credentials

Since you already have N8N working with ERPNext API, let's reuse those credentials efficiently.

### Option 1: Use HTTP Request Node Credentials
Your existing workflow likely uses an HTTP Request node with ERPNext credentials. We can reference those:

```javascript
// In the Enhanced Parser Code Node:
const API_KEY = $node["HTTP Request"].json.headers.Authorization.split(' ')[1].split(':')[0];
const API_SECRET = $node["HTTP Request"].json.headers.Authorization.split(' ')[1].split(':')[1];
```

### Option 2: Pass Credentials Through Workflow
Add a simple Code node before the Enhanced Parser that passes credentials:

```javascript
// Simple credential passthrough node:
return [{
  json: {
    ...($input.all()[0].json),
    api_key: "YOUR_EXISTING_API_KEY",
    api_secret: "YOUR_EXISTING_API_SECRET"
  }
}];
```

### Option 3: Environment Variables in N8N
Set credentials as N8N environment variables and reference them:

```javascript
const API_KEY = $vars.ERPNEXT_API_KEY;
const API_SECRET = $vars.ERPNEXT_API_SECRET;
```

## Working with PDF Text Extraction Limitations

The `Extract from File` node gives us text without layout, but we can still extract meaningful structure:

### Enhanced Text Analysis Approach

1. **Pattern Recognition**: Look for spacing patterns, indentation, and currency positions
2. **Section Identification**: Use keywords to identify different parts of the invoice
3. **Fallback Strategies**: Multiple parsing attempts with decreasing complexity

### Real-World Example

Given this extracted text from your Dutch invoice:
```
FACTUUR
Freedom Internet B.V.
Postbus 471
...
Omschrijving                     Bedrag
Internet                         € 37.19
Domeinregistratie               € 7.85
                                -------
Totaal exclusief Btw            € 37.19
Btw 21%                         € 7.85
Totaal te betalen               € 45.04
```

The enhanced parser will:
1. Detect "FACTUUR" → Start supplier section
2. Find "Freedom Internet B.V." → Extract supplier name
3. Detect "Omschrijving" → Start line items section
4. Parse amounts using currency patterns → Extract line items
5. Find totals using "Totaal" patterns → Extract financial data

## Simplified Implementation Steps

### Step 1: Test Current Workflow
First, let's see what your current N8N workflow outputs from the Extract from File node.

### Step 2: Add Debug Output
Temporarily add a debug Code node after "Extract from File":

```javascript
// Debug: See what we're working with
console.log("Raw extracted text:", $input.all()[0].json.text);

return [{
  json: {
    text_length: $input.all()[0].json.text.length,
    text_preview: $input.all()[0].json.text.substring(0, 500),
    lines_count: $input.all()[0].json.text.split('\n').length,
    has_currency: $input.all()[0].json.text.includes('€'),
    has_dutch_keywords: $input.all()[0].json.text.match(/factuur|btw|totaal/i) ? true : false
  }
}];
```

### Step 3: Replace with Enhanced Parser
Once we understand the text structure, replace the debug node with the enhanced parser.

### Step 4: Start Simple, Enhance Gradually
Begin with basic extraction, then add complexity:

1. **Basic**: Extract supplier name, invoice number, total amount
2. **Intermediate**: Add line item extraction  
3. **Advanced**: Add database matching and confidence scoring

## Practical Testing Script

Here's a simplified test that works with your existing setup:

```bash
#!/bin/bash
echo "🧪 Testing Enhanced Parser Integration..."

# Test with existing N8N webhook
curl -X POST "https://n8n.fivi.eu/webhook/erpnext-file-upload" \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "test-invoice.pdf",
    "file_url": "/private/files/test-invoice.pdf",
    "file_size": 48684,
    "file_type": "PDF"
  }'

echo "Check results at: https://n8n.fivi.eu/workflow/YOUR_WORKFLOW_ID/executions"
```

## Next Steps

1. **Check Current Output**: See what text the Extract from File node produces
2. **Add Credentials**: Use one of the three credential methods above
3. **Test Basic Parsing**: Start with simple field extraction
4. **Enhance Gradually**: Add more sophisticated features

Would you like me to create a simplified version that starts with just the basic fields (supplier, amount, date) and builds from there?
