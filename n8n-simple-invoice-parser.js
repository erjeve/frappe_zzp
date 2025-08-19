// Alternative: Simpler Invoice Parser for Manual Review
// This creates a draft Purchase Invoice with key fields extracted
// Human review required for line items and corrections

const extractedText = $input.all()[0].json.text;

function parseBasicInvoiceData(text) {
  const data = {
    supplier_name: '',
    invoice_number: '',
    invoice_date: '',
    total_incl_vat: 0,
    vat_amount: 0,
    total_excl_vat: 0
  };

  // Basic extraction - more reliable fields only
  const supplierMatch = text.match(/FACTUUR\s*\n([^\n]+)/);
  if (supplierMatch) {
    data.supplier_name = supplierMatch[1].trim();
  }

  const invoiceNumMatch = text.match(/V(\d+)/);
  if (invoiceNumMatch) {
    data.invoice_number = 'V' + invoiceNumMatch[1];
  }

  const dateMatch = text.match(/(\d{2}-\d{2}-\d{4})/);
  if (dateMatch) {
    const [day, month, year] = dateMatch[1].split('-');
    data.invoice_date = `${year}-${month}-${day}`;
  }

  // Extract clear total amounts
  const totalInclMatch = text.match(/€\s*([\d,]+\.\d{2})\s*Totaal te betalen/);
  if (totalInclMatch) {
    data.total_incl_vat = parseFloat(totalInclMatch[1].replace(',', ''));
  }

  const vatMatch = text.match(/€\s*([\d,]+\.\d{2})\s*Btw 21%/);
  if (vatMatch) {
    data.vat_amount = parseFloat(vatMatch[1].replace(',', ''));
  }

  const totalExclMatch = text.match(/€\s*([\d,]+\.\d{2})\s*Totaal exclusief Btw/);
  if (totalExclMatch) {
    data.total_excl_vat = parseFloat(totalExclMatch[1].replace(',', ''));
  }

  return data;
}

const basicData = parseBasicInvoiceData(extractedText);

// Create minimal ERPNext Purchase Invoice for manual completion
const draftInvoice = {
  doctype: "Purchase Invoice",
  supplier: basicData.supplier_name || "Unknown Supplier",
  bill_no: basicData.invoice_number || "MANUAL_ENTRY_NEEDED",
  bill_date: basicData.invoice_date || new Date().toISOString().split('T')[0],
  posting_date: new Date().toISOString().split('T')[0],
  currency: "EUR",
  net_total: basicData.total_excl_vat,
  grand_total: basicData.total_incl_vat,
  total_taxes_and_charges: basicData.vat_amount,
  // Single generic line item - to be manually updated
  items: [{
    item_code: "GENERIC-SERVICE",
    item_name: `Services from ${basicData.supplier_name}`,
    description: `Invoice ${basicData.invoice_number} - Manual review required`,
    qty: 1,
    rate: basicData.total_excl_vat,
    amount: basicData.total_excl_vat
  }],
  taxes: [{
    charge_type: "On Net Total",
    rate: 21,
    tax_amount: basicData.vat_amount,
    description: "BTW 21%",
    account_head: "VAT 21% - Company"
  }],
  // Add note for manual review
  remarks: `Auto-generated from PDF. Please review and update line items. Original text: ${extractedText.substring(0, 500)}...`
};

return [{
  json: {
    basic_data: basicData,
    draft_invoice: draftInvoice,
    needs_manual_review: true,
    extracted_text: extractedText,
    parsing_success: {
      supplier: !!basicData.supplier_name,
      invoice_number: !!basicData.invoice_number,
      date: !!basicData.invoice_date,
      amounts: !!(basicData.total_incl_vat && basicData.vat_amount)
    }
  }
}];
