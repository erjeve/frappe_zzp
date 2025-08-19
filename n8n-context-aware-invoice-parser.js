// Context-Aware Invoice Parser with ERPNext Integration and Hybrid OCR+LLM Processing
// This parser fetches ERPNext context data to improve LLM accuracy

// Configuration
const ERPNEXT_BASE_URL = 'https://frappe.fivi.eu';
const OCR_SERVICE_URL = 'https://ocr.fivi.eu';
const OLLAMA_SERVICE_URL = 'http://ollama:11434'; // Internal Docker network
const MODEL_NAME = 'llama3.2:1b'; // Using compact 1B model for memory-constrained environments

class ContextAwareInvoiceParser {
    constructor() {
        this.erpnextContext = {
            suppliers: [],
            companies: [],
            items: [],
            currencies: [],
            taxTemplates: []
        };
    }

    // Fetch ERPNext context data for better LLM accuracy
    async fetchERPNextContext() {
        try {
            console.log('🔍 Fetching ERPNext context data...');
            
            // Get suppliers
            const suppliersResponse = await $http.request({
                method: 'GET',
                url: `${ERPNEXT_BASE_URL}/api/resource/Supplier`,
                headers: {
                    'Authorization': `token ${$vars.ERPNEXT_API_KEY}:${$vars.ERPNEXT_API_SECRET}`
                },
                qs: {
                    fields: JSON.stringify(['name', 'supplier_name', 'tax_id', 'country'])
                }
            });
            this.erpnextContext.suppliers = suppliersResponse.data || [];

            // Get companies
            const companiesResponse = await $http.request({
                method: 'GET',
                url: `${ERPNEXT_BASE_URL}/api/resource/Company`,
                headers: {
                    'Authorization': `token ${$vars.ERPNEXT_API_KEY}:${$vars.ERPNEXT_API_SECRET}`
                },
                qs: {
                    fields: JSON.stringify(['name', 'company_name', 'tax_id', 'country'])
                }
            });
            this.erpnextContext.companies = companiesResponse.data || [];

            // Get items (top 500 most common)
            const itemsResponse = await $http.request({
                method: 'GET',
                url: `${ERPNEXT_BASE_URL}/api/resource/Item`,
                headers: {
                    'Authorization': `token ${$vars.ERPNEXT_API_KEY}:${$vars.ERPNEXT_API_SECRET}`
                },
                qs: {
                    fields: JSON.stringify(['name', 'item_name', 'item_code', 'item_group']),
                    limit: 500
                }
            });
            this.erpnextContext.items = itemsResponse.data || [];

            // Get currencies
            const currenciesResponse = await $http.request({
                method: 'GET',
                url: `${ERPNEXT_BASE_URL}/api/resource/Currency`,
                headers: {
                    'Authorization': `token ${$vars.ERPNEXT_API_KEY}:${$vars.ERPNEXT_API_SECRET}`
                },
                qs: {
                    fields: JSON.stringify(['name', 'currency_name', 'symbol'])
                }
            });
            this.erpnextContext.currencies = currenciesResponse.data || [];

            // Get tax templates
            const taxResponse = await $http.request({
                method: 'GET',
                url: `${ERPNEXT_BASE_URL}/api/resource/Sales Taxes and Charges Template`,
                headers: {
                    'Authorization': `token ${$vars.ERPNEXT_API_KEY}:${$vars.ERPNEXT_API_SECRET}`
                },
                qs: {
                    fields: JSON.stringify(['name', 'title'])
                }
            });
            this.erpnextContext.taxTemplates = taxResponse.data || [];

            console.log(`✅ Context loaded: ${this.erpnextContext.suppliers.length} suppliers, ${this.erpnextContext.companies.length} companies, ${this.erpnextContext.items.length} items`);
            
            return this.erpnextContext;
        } catch (error) {
            console.error('❌ Failed to fetch ERPNext context:', error.message);
            return this.erpnextContext; // Return empty context if API fails
        }
    }

    // Extract text using OCR service with positional data
    async extractTextWithOCR(pdfBuffer) {
        try {
            console.log('🔍 Processing PDF with OCR service...');
            
            const formData = {
                file: {
                    value: pdfBuffer,
                    options: {
                        filename: 'invoice.pdf',
                        contentType: 'application/pdf'
                    }
                }
            };

            const ocrResponse = await $http.request({
                method: 'POST',
                url: `${OCR_SERVICE_URL}/process_invoice`,
                formData: formData,
                timeout: 30000
            });

            if (ocrResponse.success && ocrResponse.text) {
                console.log('✅ OCR extraction successful');
                return {
                    text: ocrResponse.text,
                    coordinates: ocrResponse.coordinates || [],
                    tables: ocrResponse.tables || [],
                    layout: ocrResponse.layout || {}
                };
            } else {
                throw new Error('OCR processing failed');
            }
        } catch (error) {
            console.error('❌ OCR extraction failed:', error.message);
            throw error;
        }
    }

    // Process invoice with LLM using ERPNext context
    async processWithLLM(ocrData, context) {
        try {
            console.log('🤖 Processing with LLM using ERPNext context...');

            // Build context-aware prompt
            const contextPrompt = this.buildContextPrompt(context);
            const structuredPrompt = this.buildStructuredPrompt(ocrData.text, contextPrompt);

            const llmResponse = await $http.request({
                method: 'POST',
                url: `${OLLAMA_SERVICE_URL}/api/generate`,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: {
                    model: MODEL_NAME,
                    prompt: structuredPrompt,
                    stream: false,
                    options: {
                        temperature: 0.1, // Low temperature for consistency
                        top_p: 0.9,
                        num_predict: 2000
                    }
                },
                timeout: 60000
            });

            if (llmResponse.response) {
                // Parse JSON response from LLM
                const jsonMatch = llmResponse.response.match(/\{[\s\S]*\}/);
                if (jsonMatch) {
                    const parsedData = JSON.parse(jsonMatch[0]);
                    console.log('✅ LLM processing successful');
                    return parsedData;
                } else {
                    throw new Error('LLM did not return valid JSON');
                }
            } else {
                throw new Error('LLM processing failed');
            }
        } catch (error) {
            console.error('❌ LLM processing failed:', error.message);
            // Fallback to basic parsing if LLM fails
            return this.fallbackParsing(ocrData.text);
        }
    }

    // Build context prompt with ERPNext data
    buildContextPrompt(context) {
        let prompt = "\n\nCONTEXT DATA FROM ERPNEXT:\n";
        
        // Add suppliers context
        if (context.suppliers.length > 0) {
            prompt += "\nKNOWN SUPPLIERS:\n";
            context.suppliers.slice(0, 20).forEach(supplier => {
                prompt += `- ${supplier.supplier_name || supplier.name}`;
                if (supplier.tax_id) prompt += ` (VAT: ${supplier.tax_id})`;
                if (supplier.country) prompt += ` [${supplier.country}]`;
                prompt += "\n";
            });
        }

        // Add companies context
        if (context.companies.length > 0) {
            prompt += "\nKNOWN COMPANIES:\n";
            context.companies.forEach(company => {
                prompt += `- ${company.company_name || company.name}`;
                if (company.tax_id) prompt += ` (VAT: ${company.tax_id})`;
                if (company.country) prompt += ` [${company.country}]`;
                prompt += "\n";
            });
        }

        // Add common items context
        if (context.items.length > 0) {
            prompt += "\nKNOWN ITEMS/SERVICES:\n";
            context.items.slice(0, 30).forEach(item => {
                prompt += `- ${item.item_name || item.name}`;
                if (item.item_code) prompt += ` (${item.item_code})`;
                if (item.item_group) prompt += ` [${item.item_group}]`;
                prompt += "\n";
            });
        }

        // Add currencies
        if (context.currencies.length > 0) {
            prompt += "\nSUPPORTED CURRENCIES:\n";
            context.currencies.forEach(currency => {
                prompt += `- ${currency.name}`;
                if (currency.symbol) prompt += ` (${currency.symbol})`;
                prompt += "\n";
            });
        }

        prompt += "\nINSTRUCTIONS: Use this context to match invoice data to existing ERPNext records. Prefer exact matches for supplier names, company names, and item codes.";
        
        return prompt;
    }

    // Build structured prompt for LLM
    buildStructuredPrompt(invoiceText, contextPrompt) {
        return `You are an expert invoice data extraction system. Extract structured data from the following invoice text and return ONLY a valid JSON object.

INVOICE TEXT:
${invoiceText}

${contextPrompt}

Extract the following information and return as JSON:
{
    "invoice_number": "string",
    "invoice_date": "YYYY-MM-DD",
    "due_date": "YYYY-MM-DD",
    "supplier": {
        "name": "string (match to known suppliers if possible)",
        "address": "string",
        "tax_id": "string",
        "country": "string"
    },
    "customer": {
        "name": "string (match to known companies if possible)",
        "address": "string",
        "tax_id": "string"
    },
    "currency": "string (use currency code from supported currencies)",
    "line_items": [
        {
            "description": "string (match to known items if possible)",
            "item_code": "string (if available)",
            "quantity": number,
            "unit_price": number,
            "tax_rate": number,
            "amount": number
        }
    ],
    "tax_summary": {
        "total_before_tax": number,
        "total_tax": number,
        "total_amount": number
    },
    "payment_terms": "string",
    "reference_number": "string",
    "confidence_score": number (0-1),
    "matched_records": {
        "supplier_matched": boolean,
        "customer_matched": boolean,
        "items_matched": number
    }
}

CRITICAL: Return ONLY the JSON object, no additional text or explanation.`;
    }

    // Fallback parsing if LLM fails
    fallbackParsing(text) {
        console.log('⚠️ Using fallback parsing method');
        
        // Basic regex patterns for fallback
        const invoiceNumberMatch = text.match(/(?:invoice|factuur|nummer|number)[:\s#]*([A-Z0-9-]+)/i);
        const amountMatch = text.match(/(?:total|totaal)[:\s]*[€$£]?\s*([0-9,.]+)/i);
        const dateMatch = text.match(/(\d{1,2}[-\/\.]\d{1,2}[-\/\.]\d{2,4})/);

        return {
            invoice_number: invoiceNumberMatch ? invoiceNumberMatch[1] : null,
            invoice_date: dateMatch ? dateMatch[1] : null,
            supplier: { name: "Unknown" },
            customer: { name: "Unknown" },
            currency: "EUR",
            line_items: [],
            tax_summary: {
                total_amount: amountMatch ? parseFloat(amountMatch[1].replace(',', '.')) : 0
            },
            confidence_score: 0.3,
            matched_records: {
                supplier_matched: false,
                customer_matched: false,
                items_matched: 0
            }
        };
    }

    // Main processing function
    async processInvoice(pdfBuffer) {
        try {
            console.log('🚀 Starting context-aware invoice processing...');
            
            // Step 1: Fetch ERPNext context
            const context = await this.fetchERPNextContext();
            
            // Step 2: Extract text with OCR
            const ocrData = await this.extractTextWithOCR(pdfBuffer);
            
            // Step 3: Process with LLM using context
            const structuredData = await this.processWithLLM(ocrData, context);
            
            // Step 4: Enhance with OCR positional data if needed
            structuredData.ocr_metadata = {
                coordinates_available: ocrData.coordinates.length > 0,
                tables_detected: ocrData.tables.length,
                processing_method: 'hybrid_ocr_llm'
            };
            
            console.log('✅ Invoice processing complete');
            return structuredData;
            
        } catch (error) {
            console.error('❌ Invoice processing failed:', error.message);
            throw error;
        }
    }
}

// N8N Workflow Integration
const parser = new ContextAwareInvoiceParser();

// Get PDF from previous node
const inputData = $input.all();
const pdfBuffer = inputData[0].binary.data.data;

// Process invoice
const result = await parser.processInvoice(pdfBuffer);

// Return structured result for ERPNext creation
return [{ json: result }];
