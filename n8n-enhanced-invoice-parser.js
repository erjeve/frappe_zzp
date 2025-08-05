// Enhanced Invoice Parser with Layout Recognition and ERPNext Integration
// Uses position-aware parsing, database matching, and structured validation

const extractedText = $input.all()[0].json.text;

// Configuration for ERPNext API
const ERPNEXT_BASE_URL = 'https://frappe.fivi.eu';
// Reuse existing N8N ERPNext credentials
// Check multiple possible sources for API credentials
const API_KEY = 
  $input.all()[0].json.api_key || 
  $node["HTTP Request"].parameter.authentication?.apiKey ||
  $workflow.settings?.variables?.erpnext_api_key ||
  '';
  
const API_SECRET = 
  $input.all()[0].json.api_secret ||
  $node["HTTP Request"].parameter.authentication?.apiSecret ||
  $workflow.settings?.variables?.erpnext_api_secret ||
  '';

class InvoiceLayoutParser {
  constructor(text) {
    this.text = text;
    this.lines = text.split('\n').filter(line => line.trim());
    this.sections = this.identifySections();
    this.layoutHints = this.analyzeTextLayout();
  }

  analyzeTextLayout() {
    // Analyze text patterns to understand layout without position data
    const hints = {
      hasTableStructure: false,
      columnSeparators: [],
      indentationLevels: [],
      currencyPositions: [],
      numberPatterns: []
    };

    this.lines.forEach((line, index) => {
      const trimmed = line.trim();
      
      // Detect table-like structures by looking for multiple currency amounts
      const euroMatches = (trimmed.match(/€\s*[\d,]+\.\d{2}/g) || []);
      if (euroMatches.length > 1) {
        hints.hasTableStructure = true;
        hints.currencyPositions.push({
          line: index,
          positions: euroMatches.map(match => line.indexOf(match))
        });
      }

      // Detect indentation patterns (common in invoices)
      const leadingSpaces = line.length - line.trimLeft().length;
      if (leadingSpaces > 0 && trimmed.length > 0) {
        hints.indentationLevels.push(leadingSpaces);
      }

      // Look for column separators (multiple spaces, tabs)
      const multiSpaces = trimmed.match(/\s{3,}/g);
      if (multiSpaces) {
        hints.columnSeparators.push({
          line: index,
          separators: multiSpaces.length
        });
      }

      // Identify number patterns (quantities, prices)
      const numberPattern = trimmed.match(/\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b/g);
      if (numberPattern) {
        hints.numberPatterns.push({
          line: index,
          numbers: numberPattern
        });
      }
    });

    return hints;
  }

  identifySections() {
    const sections = {
      header: [],
      supplier: [],
      invoice_details: [],
      line_items: [],
      totals: [],
      footer: []
    };

    let currentSection = 'header';
    
    this.lines.forEach((line, index) => {
      const trimmed = line.trim();
      
      // Section identification patterns
      if (trimmed.match(/FACTUUR|INVOICE/i)) {
        currentSection = 'supplier';
        sections.supplier.push({line: trimmed, index, confidence: 0.9});
      } else if (trimmed.match(/Factuurnummer|Invoice.*Number|V\d+/i)) {
        currentSection = 'invoice_details';
        sections.invoice_details.push({line: trimmed, index, confidence: 0.8});
      } else if (trimmed.match(/Omschrijving|Description|Product|Service/i)) {
        currentSection = 'line_items';
        sections.line_items.push({line: trimmed, index, confidence: 0.7});
      } else if (trimmed.match(/Totaal|Total|Btw|VAT|€.*\d+\.\d{2}/)) {
        currentSection = 'totals';
        sections.totals.push({line: trimmed, index, confidence: 0.8});
      } else {
        sections[currentSection].push({line: trimmed, index, confidence: 0.5});
      }
    });

    return sections;
  }

  extractSupplierInfo() {
    // Look for supplier in header/supplier sections
    const supplierCandidates = [];
    
    [...this.sections.header, ...this.sections.supplier].forEach(item => {
      const line = item.line;
      
      // Skip obvious non-supplier lines
      if (line.match(/FACTUUR|Datum|Date|Pagina|Page/i)) return;
      
      // Company name patterns (Dutch)
      if (line.match(/B\.V\.|BV|N\.V\.|NV|VOF|CV|Holding|Group|Company/i)) {
        supplierCandidates.push({
          name: line.trim(),
          confidence: 0.9,
          type: 'company_suffix'
        });
      }
      
      // First substantial line after FACTUUR
      if (item.index > 0 && this.lines[item.index - 1].match(/FACTUUR/i)) {
        supplierCandidates.push({
          name: line.trim(),
          confidence: 0.8,
          type: 'after_invoice_header'
        });
      }
    });

    return supplierCandidates.sort((a, b) => b.confidence - a.confidence)[0]?.name || '';
  }

  extractLineItems() {
    const items = [];
    let inItemSection = false;
    let tableHeaderFound = false;
    
    // Use layout hints to improve extraction
    const hasTableStructure = this.layoutHints.hasTableStructure;
    const commonIndent = this.layoutHints.indentationLevels.length > 0 ? 
      Math.min(...this.layoutHints.indentationLevels) : 0;
    
    this.sections.line_items.forEach((item, index) => {
      const line = item.line;
      const originalLine = this.lines[item.index]; // Keep original spacing
      
      // Start of items section
      if (line.match(/Omschrijving|Description|Product|Service/i)) {
        inItemSection = true;
        tableHeaderFound = true;
        return;
      }
      
      if (inItemSection) {
        // Stop at totals
        if (line.match(/Subtotaal|Totaal|BTW|VAT|Te betalen/i)) {
          inItemSection = false;
          return;
        }
        
        // Enhanced extraction using layout hints
        if (hasTableStructure) {
          // Try table-based extraction
          const tableItem = this.extractFromTableStructure(originalLine, line);
          if (tableItem) {
            items.push({...tableItem, confidence: 0.8});
            return;
          }
        }
        
        // Try standard patterns
        const itemMatch = line.match(/^(.+?)\s+(\d+(?:\.\d+)?)\s+€\s*([\d,]+\.\d{2})\s*€\s*([\d,]+\.\d{2})$/);
        if (itemMatch) {
          items.push({
            description: itemMatch[1].trim(),
            quantity: parseFloat(itemMatch[2]),
            unit_price: parseFloat(itemMatch[3].replace(',', '')),
            total: parseFloat(itemMatch[4].replace(',', '')),
            confidence: 0.8
          });
        } else {
          // Enhanced fallback using currency detection
          const euroMatches = line.match(/€\s*([\d,]+\.\d{2})/g);
          if (euroMatches && euroMatches.length >= 1) {
            // Extract description (everything before first currency)
            const firstEuroPos = line.indexOf('€');
            const description = line.substring(0, firstEuroPos).trim();
            
            if (description.length > 3) { // Minimum description length
              const amount = parseFloat(euroMatches[0].replace('€', '').replace(',', '').trim());
              
              // Look for quantity in the description or assume 1
              const qtyMatch = description.match(/(\d+(?:\.\d+)?)\s*x\s*(.+)/i);
              let quantity = 1;
              let itemDesc = description;
              
              if (qtyMatch) {
                quantity = parseFloat(qtyMatch[1]);
                itemDesc = qtyMatch[2].trim();
              }
              
              items.push({
                description: itemDesc,
                quantity: quantity,
                unit_price: amount / quantity,
                total: amount,
                confidence: 0.6
              });
            }
          }
        }
      }
    });

    return items;
  }

  extractFromTableStructure(originalLine, trimmedLine) {
    // Try to extract from table-like structure using spacing
    const parts = originalLine.split(/\s{2,}/); // Split on 2+ spaces
    
    if (parts.length >= 3) {
      // Likely format: Description | Qty | Price | Total
      // or: Description | Price | Total
      
      const description = parts[0].trim();
      if (description.length < 3) return null;
      
      // Find currency amounts in the parts
      const amountParts = parts.slice(1).filter(part => part.match(/€\s*[\d,]+\.\d{2}/));
      
      if (amountParts.length >= 1) {
        const amounts = amountParts.map(part => 
          parseFloat(part.replace('€', '').replace(',', '').trim())
        );
        
        if (amounts.length === 1) {
          // Just one amount - probably total
          return {
            description: description,
            quantity: 1,
            unit_price: amounts[0],
            total: amounts[0]
          };
        } else if (amounts.length >= 2) {
          // Multiple amounts - likely unit price and total
          const unitPrice = amounts[amounts.length - 2];
          const total = amounts[amounts.length - 1];
          const quantity = Math.round((total / unitPrice) * 100) / 100; // Round to 2 decimals
          
          return {
            description: description,
            quantity: quantity || 1,
            unit_price: unitPrice,
            total: total
          };
        }
      }
    }
    
    return null;
  }

  extractTotals() {
    const totals = {};
    
    this.sections.totals.forEach(item => {
      const line = item.line;
      
      // Various total patterns
      const patterns = [
        { key: 'subtotal', regex: /(?:Subtotaal|Totaal exclusief.*btw).*€\s*([\d,]+\.\d{2})/i },
        { key: 'vat_amount', regex: /(?:Btw|VAT).*21%.*€\s*([\d,]+\.\d{2})/i },
        { key: 'total', regex: /(?:Totaal te betalen|Grand total|Total incl).*€\s*([\d,]+\.\d{2})/i }
      ];
      
      patterns.forEach(pattern => {
        const match = line.match(pattern.regex);
        if (match && !totals[pattern.key]) {
          totals[pattern.key] = parseFloat(match[1].replace(',', ''));
        }
      });
    });

    return totals;
  }
}

// ERPNext Database Integration
class ERPNextMatcher {
  constructor(baseUrl, apiKey, apiSecret) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
    this.apiSecret = apiSecret;
  }

  async searchSuppliers(supplierName) {
    if (!supplierName) return [];
    
    try {
      const response = await fetch(`${this.baseUrl}/api/resource/Supplier?filters=[["supplier_name","like","%${supplierName}%"]]&limit=5`, {
        headers: {
          'Authorization': `token ${this.apiKey}:${this.apiSecret}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        return data.data.map(supplier => ({
          name: supplier.name,
          supplier_name: supplier.supplier_name,
          match_score: this.calculateMatchScore(supplierName, supplier.supplier_name)
        }));
      }
    } catch (error) {
      console.log('Supplier search error:', error);
    }
    
    return [];
  }

  async searchItems(description) {
    if (!description) return [];
    
    try {
      const response = await fetch(`${this.baseUrl}/api/resource/Item?filters=[["item_name","like","%${description}%"]]&limit=5`, {
        headers: {
          'Authorization': `token ${this.apiKey}:${this.apiSecret}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        return data.data.map(item => ({
          item_code: item.name,
          item_name: item.item_name,
          match_score: this.calculateMatchScore(description, item.item_name)
        }));
      }
    } catch (error) {
      console.log('Item search error:', error);
    }
    
    return [];
  }

  calculateMatchScore(text1, text2) {
    // Simple fuzzy matching score
    const words1 = text1.toLowerCase().split(/\s+/);
    const words2 = text2.toLowerCase().split(/\s+/);
    
    let matches = 0;
    words1.forEach(word1 => {
      if (words2.some(word2 => word2.includes(word1) || word1.includes(word2))) {
        matches++;
      }
    });
    
    return matches / Math.max(words1.length, words2.length);
  }
}

// Main processing function
async function processInvoice() {
  const parser = new InvoiceLayoutParser(extractedText);
  const matcher = new ERPNextMatcher(ERPNEXT_BASE_URL, API_KEY, API_SECRET);

  // Extract basic data
  const supplierName = parser.extractSupplierInfo();
  const lineItems = parser.extractLineItems();
  const totals = parser.extractTotals();

  // Search for existing suppliers
  const supplierMatches = await matcher.searchSuppliers(supplierName);

  // Search for existing items
  const itemMatches = await Promise.all(
    lineItems.map(async item => ({
      ...item,
      existing_items: await matcher.searchItems(item.description)
    }))
  );

  // Extract invoice metadata
  const invoiceNumber = extractedText.match(/V(\d+)/)?.[1] ? `V${extractedText.match(/V(\d+)/)[1]}` : '';
  const dateMatch = extractedText.match(/(\d{2}-\d{2}-\d{4})/);
  const invoiceDate = dateMatch ? 
    dateMatch[1].split('-').reverse().join('-') : 
    new Date().toISOString().split('T')[0];

  // Create structured result with human review requirements
  const result = {
    extracted_data: {
      supplier_name: supplierName,
      invoice_number: invoiceNumber,
      invoice_date: invoiceDate,
      line_items: itemMatches,
      totals: totals
    },
    database_matches: {
      suppliers: supplierMatches,
      high_confidence_supplier: supplierMatches.find(s => s.match_score > 0.8)
    },
    human_review_required: {
      supplier_creation: supplierMatches.length === 0 || !supplierMatches.some(s => s.match_score > 0.8),
      item_mappings: itemMatches.filter(item => 
        !item.existing_items.length || !item.existing_items.some(ei => ei.match_score > 0.7)
      ),
      manual_verification: lineItems.some(item => item.confidence < 0.7)
    },
    suggested_actions: [],
    confidence_score: calculateOverallConfidence(supplierMatches, itemMatches, totals)
  };

  // Generate suggestions
  if (result.human_review_required.supplier_creation) {
    result.suggested_actions.push({
      type: 'create_supplier',
      data: { supplier_name: supplierName },
      priority: 'high'
    });
  }

  result.human_review_required.item_mappings.forEach(item => {
    result.suggested_actions.push({
      type: 'map_or_create_item',
      data: {
        description: item.description,
        suggested_matches: item.existing_items
      },
      priority: 'medium'
    });
  });

  return result;
}

function calculateOverallConfidence(supplierMatches, itemMatches, totals) {
  let score = 0;
  let factors = 0;

  // Supplier confidence
  if (supplierMatches.length > 0 && supplierMatches[0].match_score > 0.8) {
    score += 0.3;
  }
  factors += 0.3;

  // Items confidence
  const avgItemConfidence = itemMatches.reduce((sum, item) => sum + item.confidence, 0) / itemMatches.length;
  score += avgItemConfidence * 0.4;
  factors += 0.4;

  // Totals confidence
  if (totals.total && totals.vat_amount) {
    score += 0.3;
  }
  factors += 0.3;

  return score / factors;
}

// Execute and return result
return processInvoice().then(result => [{
  json: {
    ...result,
    raw_text: extractedText,
    layout_sections: new InvoiceLayoutParser(extractedText).sections
  }
}]).catch(error => [{
  json: {
    error: error.message,
    raw_text: extractedText,
    fallback_mode: true
  }
}]);
