// N8N Code Node: Parse Dutch Invoice Data (Robust Version)
// Add this as a Code node after "Extract from File"

const extractedText = $input.all()[0].json.text;
console.log('Extracted text:', extractedText);

// More robust parsing with better VAT handling
function parseInvoiceData(text) {
  const data = {
    supplier_name: '',
    invoice_number: '',
    invoice_date: '',
    total_amount_incl_vat: 0,
    vat_amount: 0,
    total_amount_excl_vat: 0,
    line_items: [],
    currency: 'EUR'
  };

  // Extract supplier name (line after FACTUUR)
  const supplierMatch = text.match(/FACTUUR\s*\n([^\n]+)/);
  if (supplierMatch) {
    data.supplier_name = supplierMatch[1].trim();
  }

  // Extract invoice number (V followed by numbers)
  const invoiceNumMatch = text.match(/V(\d+)/);
  if (invoiceNumMatch) {
    data.invoice_number = 'V' + invoiceNumMatch[1];
  }

  // Extract invoice date (DD-MM-YYYY format)
  const dateMatch = text.match(/(\d{2}-\d{2}-\d{4})/);
  if (dateMatch) {
    const [day, month, year] = dateMatch[1].split('-');
    data.invoice_date = `${year}-${month}-${day}`;
  }

  // Extract amounts with more flexible patterns
  // "Totaal te betalen" = Total including VAT
  const totalInclMatch = text.match(/€\s*([\d,]+\.\d{2})\s*Totaal te betalen/);
  if (totalInclMatch) {
    data.total_amount_incl_vat = parseFloat(totalInclMatch[1].replace(',', ''));
  }

  // "Btw 21%" = VAT amount
  const vatMatch = text.match(/€\s*([\d,]+\.\d{2})\s*Btw 21%/);
  if (vatMatch) {
    data.vat_amount = parseFloat(vatMatch[1].replace(',', ''));
  }

  // "Totaal exclusief Btw" = Total excluding VAT
  const totalExclMatch = text.match(/€\s*([\d,]+\.\d{2})\s*Totaal exclusief Btw/);
  if (totalExclMatch) {
    data.total_amount_excl_vat = parseFloat(totalExclMatch[1].replace(',', ''));
  }

  // Fallback calculations if any amount is missing
  if (data.total_amount_incl_vat && data.vat_amount && !data.total_amount_excl_vat) {
    data.total_amount_excl_vat = data.total_amount_incl_vat - data.vat_amount;
  }
  if (data.total_amount_excl_vat && data.vat_amount && !data.total_amount_incl_vat) {
    data.total_amount_incl_vat = data.total_amount_excl_vat + data.vat_amount;
  }

  // Extract line items - flexible approach
  // Look for patterns like "€ 50,00€ 50,00Internet glasvezel..."
  const lineItemPattern = /€\s*([\d,]+\.\d{2})\s*€\s*([\d,]+\.\d{2})\s*([^€\n]+?)(?=€|\n|$)/g;
  let match;
  
  while ((match = lineItemPattern.exec(text)) !== null) {
    const unitPrice = parseFloat(match[1].replace(',', ''));
    const totalPrice = parseFloat(match[2].replace(',', ''));
    let description = match[3].trim();
    
    // Clean up description - remove dates and extra text
    description = description.replace(/\s+Maand\s+\d{1,2}-\d{1,2}-\d{4}\s+\d{1,2}-\d{1,2}-\d{4}/, '').trim();
    
    // Skip empty descriptions or totals
    if (description && 
        !description.toLowerCase().includes('totaal') && 
        !description.toLowerCase().includes('btw') &&
        totalPrice > 0) {
      
      data.line_items.push({
        description: description,
        qty: totalPrice / unitPrice || 1, // Calculate quantity
        rate_incl_vat: unitPrice,
        amount_incl_vat: totalPrice,
        // Calculate excluding VAT (assuming 21% VAT)
        rate_excl_vat: parseFloat((unitPrice / 1.21).toFixed(2)),
        amount_excl_vat: parseFloat((totalPrice / 1.21).toFixed(2))
      });
    }
  }

  // If no line items found, create a generic one
  if (data.line_items.length === 0 && data.total_amount_excl_vat > 0) {
    data.line_items.push({
      description: `Services from ${data.supplier_name}`,
      qty: 1,
      rate_incl_vat: data.total_amount_incl_vat,
      amount_incl_vat: data.total_amount_incl_vat,
      rate_excl_vat: data.total_amount_excl_vat,
      amount_excl_vat: data.total_amount_excl_vat
    });
  }

  return data;
}

// Parse the invoice
const invoiceData = parseInvoiceData(extractedText);

// Prepare ERPNext Purchase Invoice data (amounts excluding VAT as ERPNext standard)
const erpnextData = {
  doctype: "Purchase Invoice",
  supplier: invoiceData.supplier_name || "Freedom Internet B.V.",
  bill_no: invoiceData.invoice_number,
  bill_date: invoiceData.invoice_date,
  posting_date: new Date().toISOString().split('T')[0],
  due_date: invoiceData.invoice_date,
  currency: invoiceData.currency,
  // ERPNext typically works with amounts excluding tax
  net_total: invoiceData.total_amount_excl_vat,
  grand_total: invoiceData.total_amount_incl_vat,
  total_taxes_and_charges: invoiceData.vat_amount,
  items: invoiceData.line_items.map((item, index) => ({
    item_code: `ITEM-${index + 1}`, // Generic item code
    item_name: item.description,
    description: item.description,
    qty: item.qty,
    rate: item.rate_excl_vat, // Rate excluding VAT
    amount: item.amount_excl_vat // Amount excluding VAT
  })),
  taxes: [{
    charge_type: "On Net Total",
    rate: 21, // 21% VAT
    tax_amount: invoiceData.vat_amount,
    description: "BTW 21%",
    account_head: "VAT 21% - Company" // Adjust to your chart of accounts
  }]
};

return [{
  json: {
    parsed_invoice: invoiceData,
    erpnext_data: erpnextData,
    original_text: extractedText,
    debug_info: {
      supplier_found: !!invoiceData.supplier_name,
      invoice_number_found: !!invoiceData.invoice_number,
      date_found: !!invoiceData.invoice_date,
      amounts_found: {
        incl_vat: !!invoiceData.total_amount_incl_vat,
        excl_vat: !!invoiceData.total_amount_excl_vat,
        vat: !!invoiceData.vat_amount
      },
      line_items_count: invoiceData.line_items.length
    }
  }
}];
