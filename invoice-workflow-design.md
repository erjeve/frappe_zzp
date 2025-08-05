# Human-in-the-Loop Invoice Processing Workflow

## Overview
This document outlines the enhanced invoice processing workflow that addresses:
1. **Layout Recognition**: Better understanding of document structure
2. **Database Matching**: Integration with existing ERPNext data
3. **LLM Processing**: Structured output using local Llama models
4. **Human Validation**: Approval process for uncertain data

## Workflow Steps

### 1. File Upload & Webhook Trigger
```
ERPNext File Upload → Webhook → N8N
```
- Webhook sends: file_url, api_key, api_secret, user_info
- N8N receives notification of new invoice

### 2. File Download & Text Extraction
```
HTTP Request (ERPNext API) → Extract from File → Raw Text
```
- Downloads PDF using ERPNext API authentication
- Extracts text content (preserves some layout via line breaks)

### 3. Multi-Stage Parsing (Choose One)

#### Option A: Enhanced Layout Parser
```
Code Node: n8n-enhanced-invoice-parser.js
```
- **Pros**: Fast, reliable for standard formats, database integration
- **Cons**: Limited flexibility for complex layouts

#### Option B: LLM-Powered Parser  
```
Code Node: n8n-llm-invoice-parser.js → Ollama API
```
- **Pros**: Handles complex layouts, multilingual, contextual understanding
- **Cons**: Requires local LLM setup, slower processing

### 4. Database Validation & Matching
```
ERPNext API Calls: Supplier Search, Item Search
```
- Searches existing suppliers by name similarity
- Matches line items to existing Item master
- Returns confidence scores for matches

### 5. Human Review Decision Tree

#### Auto-Approve (High Confidence)
- Supplier match > 80%
- All line items matched > 70%  
- Math validation passes
- Overall confidence > 85%

**Action**: Create Purchase Invoice directly

#### Require Review (Medium Confidence)
- Supplier match 50-80% OR new supplier needed
- Some line items unmatched
- Minor math discrepancies
- Overall confidence 60-85%

**Action**: Create draft + send notification for review

#### Manual Processing (Low Confidence)
- Supplier match < 50%
- Multiple line items unmatched
- Math errors detected
- Overall confidence < 60%

**Action**: Create basic draft + flag for manual entry

### 6. Review Interface Options

#### Option A: ERPNext Native
- Create draft Purchase Invoice with validation notes
- Use ERPNext's review/approval workflow
- Comments field contains parsing details

#### Option B: N8N Form (Recommended)
- Generate review form URL
- Email/notify user with review link
- Collect corrections and approvals
- Update ERPNext after approval

#### Option C: External Interface
- Custom web interface for invoice review
- Side-by-side PDF and form view
- Integration back to ERPNext via API

## Implementation Priority

### Phase 1: Foundation (1-2 days)
1. ✅ Basic N8N integration working
2. ✅ PDF download and text extraction
3. 🔄 Enhanced layout parser (n8n-enhanced-invoice-parser.js)
4. 🔄 ERPNext database matching

### Phase 2: LLM Integration (2-3 days)
1. Install Ollama (`./install-ollama.sh`)
2. Test LLM parser (n8n-llm-invoice-parser.js)
3. Compare accuracy vs enhanced parser
4. Optimize prompts for Dutch invoices

### Phase 3: Human Review (3-4 days)
1. Implement confidence scoring
2. Create review notification system
3. Build approval workflow
4. Test end-to-end process

### Phase 4: Production Optimization (1-2 days)
1. Error handling and retry logic
2. Performance monitoring
3. User training and documentation
4. Backup manual process

## Configuration Examples

### N8N Workflow Structure
```
1. Webhook (Trigger)
2. HTTP Request (Download PDF)
3. Extract from File (Get text)
4. Code (Parse invoice) ← Choose enhanced or LLM version
5. Switch (Based on confidence score)
   ├─ High Confidence → HTTP Request (Create Invoice)
   ├─ Medium Confidence → HTTP Request (Create Draft) + Email notification
   └─ Low Confidence → HTTP Request (Create Basic Draft) + Manual flag
```

### ERPNext Webhook Configuration
```json
{
  "webhook_url": "https://n8n.fivi.eu/webhook/invoice-upload",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "data": {
    "file_url": "{{ doc.file_url }}",
    "file_name": "{{ doc.file_name }}",
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "user": "{{ frappe.session.user }}",
    "timestamp": "{{ frappe.utils.now() }}"
  }
}
```

## Testing Strategy

### Test Cases
1. **Perfect Invoice**: Clear layout, existing supplier, standard items
2. **New Supplier**: Unknown supplier, require creation approval
3. **Complex Layout**: Multi-page, table formatting issues  
4. **Math Errors**: Line items don't match totals
5. **Multilingual**: Mixed Dutch/English content
6. **Edge Cases**: Handwritten notes, poor scan quality

### Success Metrics
- **Accuracy**: >95% for amount extraction
- **Automation Rate**: >80% auto-approved
- **Processing Time**: <30 seconds per invoice
- **User Satisfaction**: Minimal manual correction needed

## Next Steps

1. **Choose parsing approach**: Enhanced vs LLM (or hybrid)
2. **Set up Ollama**: Run `./install-ollama.sh` if using LLM
3. **Test database matching**: Verify supplier/item search works
4. **Design review process**: Decide on ERPNext vs external interface
5. **Implement confidence scoring**: Fine-tune approval thresholds

Would you like to proceed with any specific phase?
