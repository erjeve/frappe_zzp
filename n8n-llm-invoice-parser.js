// LLM-Powered Invoice Parser using Local Ollama/Llama
// Provides structured output with high accuracy

const extractedText = $input.all()[0].json.text;

// Configuration
const OLLAMA_BASE_URL = 'http://localhost:11434'; // Adjust if Ollama runs elsewhere
const MODEL_NAME = 'llama3.1:8b'; // or llama2, mistral, etc.

class LLMInvoiceParser {
  constructor(text) {
    this.text = text;
  }

  async parseWithLLM() {
    const prompt = this.createStructuredPrompt();
    
    try {
      const response = await fetch(`${OLLAMA_BASE_URL}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: MODEL_NAME,
          prompt: prompt,
          stream: false,
          format: 'json',
          options: {
            temperature: 0.1, // Low temperature for consistent extraction
            top_p: 0.9
          }
        })
      });

      if (response.ok) {
        const result = await response.json();
        return JSON.parse(result.response);
      } else {
        throw new Error(`LLM API error: ${response.status}`);
      }
    } catch (error) {
      console.log('LLM parsing failed, falling back to regex:', error);
      return this.fallbackParsing();
    }
  }

  createStructuredPrompt() {
    return `You are an expert invoice processing assistant. Extract structured data from this Dutch invoice text.

INVOICE TEXT:
${this.text}

Please extract the following information and return ONLY a valid JSON object with this exact structure:

{
  "supplier": {
    "name": "Company name exactly as shown",
    "address": "Full address if available",
    "vat_number": "VAT number if found",
    "confidence": 0.0-1.0
  },
  "invoice": {
    "number": "Invoice number (e.g., V12345)",
    "date": "YYYY-MM-DD format",
    "due_date": "YYYY-MM-DD format if available",
    "currency": "EUR",
    "confidence": 0.0-1.0
  },
  "line_items": [
    {
      "description": "Item or service description",
      "quantity": 1.0,
      "unit_price": 0.00,
      "total_excl_vat": 0.00,
      "vat_rate": 21,
      "vat_amount": 0.00,
      "total_incl_vat": 0.00,
      "confidence": 0.0-1.0
    }
  ],
  "totals": {
    "subtotal_excl_vat": 0.00,
    "total_vat": 0.00,
    "total_incl_vat": 0.00,
    "confidence": 0.0-1.0
  },
  "additional_info": {
    "payment_terms": "Payment terms if mentioned",
    "reference": "Any reference numbers",
    "notes": "Additional relevant information"
  }
}

IMPORTANT RULES:
1. Extract amounts exactly as shown, convert to numbers
2. Use 0.00 for missing numeric values
3. Use empty string "" for missing text values
4. Set confidence based on how clear the information is
5. For Dutch invoices: "Btw" = VAT, "Totaal" = Total
6. Include ALL line items found
7. Return ONLY the JSON object, no other text

JSON:`;
  }

  fallbackParsing() {
    // Simplified regex-based fallback
    return {
      supplier: {
        name: this.text.match(/FACTUUR\s*\n([^\n]+)/)?.[1]?.trim() || '',
        confidence: 0.6
      },
      invoice: {
        number: this.text.match(/V(\d+)/)?.[0] || '',
        date: this.extractDate(),
        currency: 'EUR',
        confidence: 0.7
      },
      line_items: this.extractSimpleItems(),
      totals: this.extractSimpleTotals(),
      additional_info: {}
    };
  }

  extractDate() {
    const match = this.text.match(/(\d{2}-\d{2}-\d{4})/);
    if (match) {
      const [day, month, year] = match[1].split('-');
      return `${year}-${month}-${day}`;
    }
    return new Date().toISOString().split('T')[0];
  }

  extractSimpleItems() {
    const items = [];
    const lines = this.text.split('\n');
    
    for (const line of lines) {
      const match = line.match(/^(.+?)\s+€\s*([\d,]+\.\d{2})$/);
      if (match && match[1].length > 5) {
        const amount = parseFloat(match[2].replace(',', ''));
        items.push({
          description: match[1].trim(),
          quantity: 1,
          unit_price: amount / 1.21, // Assume 21% VAT
          total_excl_vat: amount / 1.21,
          vat_rate: 21,
          vat_amount: amount - (amount / 1.21),
          total_incl_vat: amount,
          confidence: 0.6
        });
      }
    }
    
    return items;
  }

  extractSimpleTotals() {
    const totalMatch = this.text.match(/€\s*([\d,]+\.\d{2})\s*Totaal/);
    const vatMatch = this.text.match(/€\s*([\d,]+\.\d{2})\s*Btw/);
    
    if (totalMatch) {
      const total = parseFloat(totalMatch[1].replace(',', ''));
      const vat = vatMatch ? parseFloat(vatMatch[1].replace(',', '')) : total * 0.21 / 1.21;
      
      return {
        subtotal_excl_vat: total - vat,
        total_vat: vat,
        total_incl_vat: total,
        confidence: 0.7
      };
    }
    
    return { confidence: 0.3 };
  }
}

// Human-in-the-loop validation
class ValidationRules {
  static validate(parsedData) {
    const issues = [];
    
    // Supplier validation
    if (!parsedData.supplier.name || parsedData.supplier.confidence < 0.7) {
      issues.push({
        type: 'supplier_verification',
        message: 'Supplier name needs verification',
        data: parsedData.supplier,
        action_required: 'confirm_or_correct'
      });
    }

    // Invoice number validation
    if (!parsedData.invoice.number || parsedData.invoice.confidence < 0.8) {
      issues.push({
        type: 'invoice_number',
        message: 'Invoice number unclear',
        data: parsedData.invoice,
        action_required: 'manual_entry'
      });
    }

    // Line items validation
    parsedData.line_items.forEach((item, index) => {
      if (item.confidence < 0.6) {
        issues.push({
          type: 'line_item',
          message: `Line item ${index + 1} needs review`,
          data: item,
          action_required: 'verify_amounts'
        });
      }
    });

    // Math validation
    const calculatedTotal = parsedData.line_items.reduce((sum, item) => sum + item.total_incl_vat, 0);
    if (Math.abs(calculatedTotal - parsedData.totals.total_incl_vat) > 0.01) {
      issues.push({
        type: 'math_error',
        message: 'Line items don\'t match total',
        data: { calculated: calculatedTotal, stated: parsedData.totals.total_incl_vat },
        action_required: 'recalculate'
      });
    }

    return issues;
  }

  static getApprovalNeeded(issues) {
    return {
      requires_approval: issues.length > 0,
      blocking_issues: issues.filter(i => ['supplier_verification', 'math_error'].includes(i.type)),
      warning_issues: issues.filter(i => !['supplier_verification', 'math_error'].includes(i.type)),
      auto_approve_threshold: issues.length <= 2 && !issues.some(i => i.type === 'math_error')
    };
  }
}

// Main execution
async function processInvoiceWithLLM() {
  const parser = new LLMInvoiceParser(extractedText);
  const parsedData = await parser.parseWithLLM();
  
  // Validate results
  const validationIssues = ValidationRules.validate(parsedData);
  const approval = ValidationRules.getApprovalNeeded(validationIssues);
  
  return {
    parsed_data: parsedData,
    validation: {
      issues: validationIssues,
      approval_needed: approval,
      overall_confidence: calculateOverallConfidence(parsedData)
    },
    processing_mode: 'llm_enhanced',
    next_steps: generateNextSteps(approval, validationIssues)
  };
}

function calculateOverallConfidence(data) {
  const confidences = [
    data.supplier.confidence || 0,
    data.invoice.confidence || 0,
    data.totals.confidence || 0,
    ...data.line_items.map(item => item.confidence || 0)
  ];
  
  return confidences.reduce((sum, conf) => sum + conf, 0) / confidences.length;
}

function generateNextSteps(approval, issues) {
  if (approval.auto_approve_threshold) {
    return ['create_draft_invoice', 'auto_approve'];
  } else if (approval.requires_approval) {
    return ['create_draft_invoice', 'request_human_review', 'highlight_issues'];
  } else {
    return ['create_final_invoice'];
  }
}

// Execute and return
return processInvoiceWithLLM().then(result => [{
  json: {
    ...result,
    raw_text: extractedText,
    timestamp: new Date().toISOString()
  }
}]).catch(error => [{
  json: {
    error: error.message,
    fallback_data: new LLMInvoiceParser(extractedText).fallbackParsing(),
    processing_mode: 'fallback',
    raw_text: extractedText
  }
}]);
