// Simplified Enhanced Invoice Parser - Starter Version
// Works with plain text from "Extract from File" node
// Reuses existing N8N ERPNext credentials

const extractedText = $input.all()[0].json.text;

// Simple text-based parser - no layout assumptions
class SimpleInvoiceParser {
  constructor(text) {
    this.text = text;
    this.lines = text.split('\n').filter(line => line.trim());
  }

  extractBasicInfo() {
    const info = {
      supplier_name: '',
      invoice_number: '',
      invoice_date: '',
      currency: 'EUR',
      total_amount: 0,
      confidence: 0.5
    };

    // Extract supplier (look for company indicators)
    const supplierPatterns = [
      /FACTUUR\s*\n([^\n]+)/i,  // Line after FACTUUR
      /([A-Z][a-zA-Z\s]+(?:B\.V\.|BV|N\.V\.|NV))/,  // Company with suffix
      /^([A-Z][a-zA-Z\s&]+(?:Group|Holding|Company))/m  // Company names
    ];

    for (const pattern of supplierPatterns) {
      const match = this.text.match(pattern);
      if (match && match[1] && match[1].trim().length > 3) {
        info.supplier_name = match[1].trim();
        info.confidence += 0.2;
        break;
      }
    }

    // Extract invoice number
    const invoicePatterns = [
      /(?:Factuurnummer|Invoice.*Number|Factuur)\s*:?\s*([V]?\d+)/i,
      /\b(V\d{6,})\b/,  // V followed by 6+ digits
      /Factuur\s+([A-Z0-9-]+)/i
    ];

    for (const pattern of invoicePatterns) {
      const match = this.text.match(pattern);
      if (match && match[1]) {
        info.invoice_number = match[1].trim();
        info.confidence += 0.15;
        break;
      }
    }

    // Extract date
    const datePatterns = [
      /(\d{1,2}[-\/]\d{1,2}[-\/]\d{4})/,
      /(\d{4}[-\/]\d{1,2}[-\/]\d{1,2})/,
      /(?:Datum|Date):\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{4})/i
    ];

    for (const pattern of datePatterns) {
      const match = this.text.match(pattern);
      if (match && match[1]) {
        info.invoice_date = this.normalizeDate(match[1]);
        info.confidence += 0.1;
        break;
      }
    }

    // Extract total amount (most reliable field)
    const totalPatterns = [
      /(?:Totaal te betalen|Total to pay|Grand total).*?€\s*([\d,]+\.\d{2})/i,
      /(?:Totaal incl|Total incl).*?€\s*([\d,]+\.\d{2})/i,
      /(?:Te betalen|To pay).*?€\s*([\d,]+\.\d{2})/i,
      /€\s*([\d,]+\.\d{2})\s*(?:Totaal|Total)/i
    ];

    for (const pattern of totalPatterns) {
      const match = this.text.match(pattern);
      if (match && match[1]) {
        info.total_amount = parseFloat(match[1].replace(',', ''));
        info.confidence += 0.25;
        break;
      }
    }

    return info;
  }

  normalizeDate(dateStr) {
    // Convert various date formats to YYYY-MM-DD
    const parts = dateStr.split(/[-\/]/);
    if (parts.length === 3) {
      if (parts[0].length === 4) {
        // YYYY-MM-DD format
        return dateStr.replace(/\//g, '-');
      } else {
        // DD-MM-YYYY format
        return `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`;
      }
    }
    return new Date().toISOString().split('T')[0]; // Fallback to today
  }

  extractSimpleLineItems() {
    const items = [];
    const lines = this.text.split('\n');
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Skip empty lines and headers
      if (!line || line.match(/omschrijving|description|bedrag|amount/i)) continue;
      
      // Look for lines with currency amounts
      const match = line.match(/^(.+?)\s+€\s*([\d,]+\.\d{2})$/);
      if (match && match[1].length > 3) {
        const description = match[1].trim();
        const amount = parseFloat(match[2].replace(',', ''));
        
        // Skip total lines
        if (description.match(/totaal|total|btw|vat|subtotal/i)) continue;
        
        items.push({
          description: description,
          quantity: 1,
          rate: amount,
          amount: amount
        });
      }
    }
    
    return items;
  }
}

// Main processing
function processSimpleInvoice() {
  const parser = new SimpleInvoiceParser(extractedText);
  const basicInfo = parser.extractBasicInfo();
  const lineItems = parser.extractSimpleLineItems();
  
  // Simple validation
  const hasRequiredFields = basicInfo.supplier_name && basicInfo.total_amount > 0;
  const overallConfidence = basicInfo.confidence + (hasRequiredFields ? 0.2 : 0);
  
  return {
    extracted_data: {
      ...basicInfo,
      line_items: lineItems
    },
    confidence_score: Math.min(overallConfidence, 1.0),
    needs_review: overallConfidence < 0.7,
    processing_notes: {
      supplier_found: !!basicInfo.supplier_name,
      invoice_number_found: !!basicInfo.invoice_number,
      date_found: !!basicInfo.invoice_date,
      amount_found: basicInfo.total_amount > 0,
      line_items_count: lineItems.length
    },
    suggested_action: overallConfidence >= 0.8 ? 'auto_create' : 
                     overallConfidence >= 0.6 ? 'create_draft' : 'manual_review',
    raw_text_preview: extractedText.substring(0, 200)
  };
}

// Execute and return results
const result = processSimpleInvoice();

return [{
  json: {
    ...result,
    timestamp: new Date().toISOString(),
    parser_version: 'simple_v1.0'
  }
}];
