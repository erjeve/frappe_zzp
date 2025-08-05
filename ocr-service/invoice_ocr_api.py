#!/usr/bin/env python3
"""
Flask API server for hybrid invoice OCR processing
Combines PDF text extraction with Tesseract OCR for positional data
"""

import os
import tempfile
import json
from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import cv2
import numpy as np

app = Flask(__name__)

class HybridInvoiceProcessor:
    def __init__(self):
        self.temp_dir = "/app/temp"
        os.makedirs(self.temp_dir, exist_ok=True)

    def process_pdf(self, pdf_path, extracted_text=None):
        """
        Process PDF with hybrid approach:
        1. Extract text with coordinates using Tesseract
        2. Compare with pre-extracted text for validation
        3. Combine for enhanced accuracy
        """
        results = {
            "ocr_data": [],
            "text_validation": {},
            "layout_analysis": {},
            "extracted_fields": {},
            "confidence_scores": {}
        }

        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)
            
            for page_num, image in enumerate(images):
                page_result = self.process_page(image, page_num, extracted_text)
                results["ocr_data"].append(page_result)

            # Analyze layout and extract fields
            results["layout_analysis"] = self.analyze_layout(results["ocr_data"])
            results["extracted_fields"] = self.extract_invoice_fields(results["ocr_data"], extracted_text)
            results["text_validation"] = self.validate_with_extracted_text(results["extracted_fields"], extracted_text)
            results["confidence_scores"] = self.calculate_confidence_scores(results)

        except Exception as e:
            results["error"] = str(e)

        return results

    def process_page(self, image, page_num, extracted_text=None):
        """Process a single page with Tesseract OCR"""
        # Convert PIL image to OpenCV format for preprocessing
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Preprocessing for better OCR
        processed_image = self.preprocess_image(cv_image)
        
        # Get OCR data with coordinates
        ocr_data = pytesseract.image_to_data(
            processed_image, 
            lang='nld+eng',
            output_type=pytesseract.Output.DICT,
            config='--psm 6'  # Assume uniform block of text
        )

        # Structure the OCR data
        words = []
        lines = []
        current_line = []
        current_line_num = -1

        for i, word_text in enumerate(ocr_data['text']):
            if int(ocr_data['conf'][i]) > 30:  # Filter low confidence
                word_info = {
                    'text': word_text.strip(),
                    'confidence': int(ocr_data['conf'][i]),
                    'bbox': {
                        'x': int(ocr_data['left'][i]),
                        'y': int(ocr_data['top'][i]),
                        'width': int(ocr_data['width'][i]),
                        'height': int(ocr_data['height'][i])
                    },
                    'line_num': int(ocr_data['line_num'][i]),
                    'word_num': int(ocr_data['word_num'][i])
                }

                if word_text.strip():  # Only non-empty words
                    words.append(word_info)
                    
                    # Group words into lines
                    if ocr_data['line_num'][i] != current_line_num:
                        if current_line:
                            lines.append({
                                'line_num': current_line_num,
                                'words': current_line,
                                'text': ' '.join([w['text'] for w in current_line]),
                                'bbox': self.get_line_bbox(current_line)
                            })
                        current_line = [word_info]
                        current_line_num = ocr_data['line_num'][i]
                    else:
                        current_line.append(word_info)

        # Add last line
        if current_line:
            lines.append({
                'line_num': current_line_num,
                'words': current_line,
                'text': ' '.join([w['text'] for w in current_line]),
                'bbox': self.get_line_bbox(current_line)
            })

        return {
            'page': page_num,
            'words': words,
            'lines': lines,
            'image_size': {'width': image.width, 'height': image.height}
        }

    def preprocess_image(self, cv_image):
        """Preprocess image for better OCR results"""
        # Convert to grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        return enhanced

    def get_line_bbox(self, words):
        """Calculate bounding box for a line of words"""
        if not words:
            return {'x': 0, 'y': 0, 'width': 0, 'height': 0}
        
        min_x = min(w['bbox']['x'] for w in words)
        min_y = min(w['bbox']['y'] for w in words)
        max_x = max(w['bbox']['x'] + w['bbox']['width'] for w in words)
        max_y = max(w['bbox']['y'] + w['bbox']['height'] for w in words)
        
        return {
            'x': min_x,
            'y': min_y,
            'width': max_x - min_x,
            'height': max_y - min_y
        }

    def analyze_layout(self, ocr_data):
        """Analyze document layout to identify sections"""
        if not ocr_data or not ocr_data[0]['lines']:
            return {}

        lines = ocr_data[0]['lines']  # Assuming single page for now
        
        layout = {
            'header_region': None,
            'supplier_region': None,
            'invoice_details_region': None,
            'line_items_region': None,
            'totals_region': None,
            'table_structure': None
        }

        # Find key sections by content
        for i, line in enumerate(lines):
            text = line['text'].lower()
            
            if 'factuur' in text or 'invoice' in text:
                layout['header_region'] = {'start_line': i, 'bbox': line['bbox']}
            elif 'omschrijving' in text or 'description' in text:
                layout['line_items_region'] = {'start_line': i, 'bbox': line['bbox']}
            elif 'totaal' in text and '€' in line['text']:
                layout['totals_region'] = {'start_line': i, 'bbox': line['bbox']}

        # Analyze table structure
        layout['table_structure'] = self.detect_table_structure(lines)

        return layout

    def detect_table_structure(self, lines):
        """Detect table structure in the document"""
        table_info = {
            'has_table': False,
            'columns': [],
            'header_line': None,
            'data_lines': []
        }

        # Look for lines with multiple currency amounts (indicating table rows)
        for line in lines:
            euro_matches = len([w for w in line['words'] if '€' in w['text']])
            if euro_matches >= 2:
                table_info['has_table'] = True
                table_info['data_lines'].append(line)

        # Analyze column positions if table detected
        if table_info['has_table'] and table_info['data_lines']:
            # Find consistent x-positions across table rows
            x_positions = []
            for line in table_info['data_lines']:
                for word in line['words']:
                    if '€' in word['text'] or word['text'].replace(',', '').replace('.', '').isdigit():
                        x_positions.append(word['bbox']['x'])

            # Cluster x-positions to find columns
            if x_positions:
                x_positions.sort()
                columns = []
                current_col = x_positions[0]
                tolerance = 20  # pixels

                for x in x_positions[1:]:
                    if x - current_col > tolerance:
                        columns.append(current_col)
                        current_col = x
                columns.append(current_col)

                table_info['columns'] = columns

        return table_info

    def extract_invoice_fields(self, ocr_data, extracted_text=None):
        """Extract invoice fields using positional data"""
        fields = {
            'supplier_name': '',
            'invoice_number': '',
            'invoice_date': '',
            'line_items': [],
            'totals': {}
        }

        if not ocr_data or not ocr_data[0]['lines']:
            return fields

        lines = ocr_data[0]['lines']

        # Extract supplier (look in header region)
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            text = line['text']
            if any(suffix in text.upper() for suffix in ['B.V.', 'BV', 'N.V.', 'NV']):
                fields['supplier_name'] = text.strip()
                break

        # Extract invoice number
        for line in lines:
            text = line['text']
            if text.startswith('V') and any(c.isdigit() for c in text):
                import re
                match = re.search(r'V\d+', text)
                if match:
                    fields['invoice_number'] = match.group()
                    break

        # Extract date
        for line in lines:
            text = line['text']
            import re
            date_match = re.search(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', text)
            if date_match:
                fields['invoice_date'] = date_match.group()
                break

        # Extract line items using table structure
        table_structure = self.analyze_layout(ocr_data)['table_structure']
        if table_structure and table_structure['has_table']:
            fields['line_items'] = self.extract_table_items(table_structure['data_lines'])

        # Extract totals
        for line in lines:
            text = line['text']
            if 'totaal' in text.lower() and '€' in text:
                import re
                amount_match = re.search(r'€\s*([\d,]+\.\d{2})', text)
                if amount_match:
                    amount = float(amount_match.group(1).replace(',', ''))
                    if 'te betalen' in text.lower():
                        fields['totals']['total_amount'] = amount
                    elif 'btw' in text.lower():
                        fields['totals']['vat_amount'] = amount
                    elif 'exclusief' in text.lower():
                        fields['totals']['subtotal'] = amount

        return fields

    def extract_table_items(self, table_lines):
        """Extract line items from table structure"""
        items = []
        
        for line in table_lines:
            # Skip lines that look like totals
            if any(word in line['text'].lower() for word in ['totaal', 'btw', 'subtotal']):
                continue

            # Extract description and amounts
            words = line['words']
            description_words = []
            amounts = []

            for word in words:
                if '€' in word['text']:
                    import re
                    amount_match = re.search(r'€\s*([\d,]+\.\d{2})', word['text'])
                    if amount_match:
                        amounts.append(float(amount_match.group(1).replace(',', '')))
                elif not word['text'].replace(',', '').replace('.', '').isdigit():
                    description_words.append(word['text'])

            if description_words and amounts:
                description = ' '.join(description_words).strip()
                if len(description) > 3:  # Minimum description length
                    item = {
                        'description': description,
                        'quantity': 1,
                        'amount': amounts[-1] if amounts else 0  # Use last amount as total
                    }
                    
                    if len(amounts) > 1:
                        item['unit_price'] = amounts[0]
                        item['total'] = amounts[-1]
                    
                    items.append(item)

        return items

    def validate_with_extracted_text(self, ocr_fields, extracted_text):
        """Validate OCR results against pre-extracted text"""
        validation = {
            'supplier_match': False,
            'invoice_number_match': False,
            'amounts_match': False,
            'text_coverage': 0.0
        }

        if not extracted_text:
            return validation

        extracted_lower = extracted_text.lower()

        # Check supplier name
        if ocr_fields['supplier_name']:
            supplier_lower = ocr_fields['supplier_name'].lower()
            validation['supplier_match'] = supplier_lower in extracted_lower

        # Check invoice number
        if ocr_fields['invoice_number']:
            validation['invoice_number_match'] = ocr_fields['invoice_number'] in extracted_text

        # Check amounts
        if ocr_fields['totals'].get('total_amount'):
            amount_str = str(ocr_fields['totals']['total_amount'])
            validation['amounts_match'] = amount_str.replace('.', ',') in extracted_text or amount_str in extracted_text

        # Calculate text coverage
        ocr_words = set()
        for item in ocr_fields['line_items']:
            ocr_words.update(item['description'].lower().split())
        
        extracted_words = set(extracted_text.lower().split())
        if extracted_words:
            common_words = ocr_words.intersection(extracted_words)
            validation['text_coverage'] = len(common_words) / len(extracted_words)

        return validation

    def calculate_confidence_scores(self, results):
        """Calculate overall confidence scores"""
        scores = {
            'ocr_confidence': 0.0,
            'text_validation_score': 0.0,
            'layout_confidence': 0.0,
            'overall_confidence': 0.0
        }

        # OCR confidence (average word confidence)
        if results['ocr_data'] and results['ocr_data'][0]['words']:
            word_confidences = [w['confidence'] for w in results['ocr_data'][0]['words']]
            scores['ocr_confidence'] = sum(word_confidences) / len(word_confidences) / 100

        # Text validation score
        validation = results['text_validation']
        validation_score = 0
        validation_count = 0

        for key, value in validation.items():
            if isinstance(value, bool):
                validation_score += 1 if value else 0
                validation_count += 1
            elif key == 'text_coverage':
                validation_score += value
                validation_count += 1

        if validation_count > 0:
            scores['text_validation_score'] = validation_score / validation_count

        # Layout confidence
        layout = results['layout_analysis']
        layout_score = 0
        if layout.get('table_structure', {}).get('has_table'):
            layout_score += 0.3
        if layout.get('header_region'):
            layout_score += 0.2
        if layout.get('totals_region'):
            layout_score += 0.3
        if layout.get('line_items_region'):
            layout_score += 0.2

        scores['layout_confidence'] = layout_score

        # Overall confidence (weighted average)
        scores['overall_confidence'] = (
            scores['ocr_confidence'] * 0.4 +
            scores['text_validation_score'] * 0.4 +
            scores['layout_confidence'] * 0.2
        )

        return scores


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'hybrid-invoice-ocr'})

@app.route('/process-invoice', methods=['POST'])
def process_invoice():
    """
    Main endpoint for processing invoices
    Expects: PDF file and optional extracted text
    Returns: Structured invoice data with confidence scores
    """
    try:
        # Check if PDF file is provided
        if 'pdf_file' not in request.files:
            return jsonify({'error': 'No PDF file provided'}), 400

        pdf_file = request.files['pdf_file']
        extracted_text = request.form.get('extracted_text', '')

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir='/app/temp') as tmp_file:
            pdf_file.save(tmp_file.name)
            tmp_pdf_path = tmp_file.name

        try:
            # Process the PDF
            processor = HybridInvoiceProcessor()
            results = processor.process_pdf(tmp_pdf_path, extracted_text)

            # Clean up temporary file
            os.unlink(tmp_pdf_path)

            return jsonify(results)

        except Exception as e:
            # Clean up temporary file on error
            if os.path.exists(tmp_pdf_path):
                os.unlink(tmp_pdf_path)
            raise e

    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
