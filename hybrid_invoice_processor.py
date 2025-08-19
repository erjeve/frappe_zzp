#!/usr/bin/env python3
"""
Hybrid OCR + Text Invoice Parser
Combines Tesseract OCR (with coordinates) and extracted text for maximum accuracy
"""

import sys
import json
import tempfile
import os
from pathlib import Path
import requests
import pytesseract
from PIL import Image
import pdf2image
import fitz  # PyMuPDF
import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BoundingBox:
    left: int
    top: int 
    width: int
    height: int
    confidence: float

@dataclass
class WordData:
    text: str
    bbox: BoundingBox
    line_num: int
    block_num: int

@dataclass
class InvoiceField:
    value: str
    bbox: Optional[BoundingBox]
    confidence: float
    source: str  # 'ocr', 'text', 'hybrid'

class HybridInvoiceProcessor:
    def __init__(self, pdf_path: str, extracted_text: str):
        self.pdf_path = pdf_path
        self.extracted_text = extracted_text
        self.ocr_data = []
        self.word_map = {}
        
    def process_invoice(self) -> Dict:
        """Main processing pipeline"""
        try:
            # Step 1: Convert PDF to images
            images = self.pdf_to_images()
            
            # Step 2: Run OCR with coordinates
            for page_num, image in enumerate(images):
                ocr_result = self.run_tesseract_with_coordinates(image, page_num)
                self.ocr_data.append(ocr_result)
            
            # Step 3: Build word position map
            self.build_word_position_map()
            
            # Step 4: Extract fields using hybrid approach
            fields = self.extract_invoice_fields()
            
            # Step 5: Extract line items with position awareness
            line_items = self.extract_line_items_with_positions()
            
            return {
                "extracted_data": {
                    "supplier_name": fields.get('supplier', InvoiceField('', None, 0.0, 'none')).value,
                    "invoice_number": fields.get('invoice_number', InvoiceField('', None, 0.0, 'none')).value,
                    "invoice_date": fields.get('date', InvoiceField('', None, 0.0, 'none')).value,
                    "currency": "EUR",
                    "line_items": line_items,
                    "totals": self.extract_totals_with_positions()
                },
                "processing_info": {
                    "ocr_confidence": self.calculate_overall_ocr_confidence(),
                    "text_extraction_available": bool(self.extracted_text.strip()),
                    "hybrid_processing": True,
                    "pages_processed": len(images)
                },
                "confidence_score": self.calculate_hybrid_confidence(fields, line_items),
                "field_sources": {k: v.source for k, v in fields.items()}
            }
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return self.fallback_to_text_only()
    
    def pdf_to_images(self) -> List[Image.Image]:
        """Convert PDF to images for OCR"""
        try:
            # Use pdf2image for better quality
            images = pdf2image.convert_from_path(
                self.pdf_path,
                dpi=300,  # High DPI for better OCR
                fmt='RGB'
            )
            return images
        except Exception as e:
            logger.warning(f"pdf2image failed: {e}, trying PyMuPDF")
            # Fallback to PyMuPDF
            doc = fitz.open(self.pdf_path)
            images = []
            for page_num in range(doc.page_count):
                page = doc[page_num]
                mat = fitz.Matrix(3.0, 3.0)  # 3x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                images.append(img)
            doc.close()
            return images
    
    def run_tesseract_with_coordinates(self, image: Image.Image, page_num: int) -> Dict:
        """Run Tesseract OCR with bounding box data"""
        # Configure Tesseract for invoice processing
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz€.,%-:()[]/ '
        
        # Get detailed data with coordinates
        data = pytesseract.image_to_data(
            image, 
            config=custom_config,
            output_type=pytesseract.Output.DICT
        )
        
        words = []
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            conf = int(data['conf'][i])
            
            if text and conf > 30:  # Filter low confidence words
                bbox = BoundingBox(
                    left=data['left'][i],
                    top=data['top'][i],
                    width=data['width'][i],
                    height=data['height'][i],
                    confidence=conf / 100.0
                )
                
                word = WordData(
                    text=text,
                    bbox=bbox,
                    line_num=data['line_num'][i],
                    block_num=data['block_num'][i]
                )
                words.append(word)
        
        return {
            'page_num': page_num,
            'words': words,
            'full_text': pytesseract.image_to_string(image, config=custom_config)
        }
    
    def build_word_position_map(self):
        """Build mapping of words to their positions"""
        for page_data in self.ocr_data:
            for word in page_data['words']:
                # Normalize word for matching
                normalized = word.text.lower().strip('.,;:')
                if normalized not in self.word_map:
                    self.word_map[normalized] = []
                self.word_map[normalized].append(word)
    
    def find_word_positions(self, search_text: str) -> List[WordData]:
        """Find positions of words/phrases in OCR data"""
        normalized_search = search_text.lower().strip('.,;:')
        return self.word_map.get(normalized_search, [])
    
    def extract_invoice_fields(self) -> Dict[str, InvoiceField]:
        """Extract key fields using hybrid OCR + text approach"""
        fields = {}
        
        # Supplier extraction
        supplier_ocr = self.extract_supplier_from_ocr()
        supplier_text = self.extract_supplier_from_text()
        fields['supplier'] = self.choose_best_match('supplier', supplier_ocr, supplier_text)
        
        # Invoice number
        invoice_ocr = self.extract_invoice_number_from_ocr()
        invoice_text = self.extract_invoice_number_from_text()
        fields['invoice_number'] = self.choose_best_match('invoice_number', invoice_ocr, invoice_text)
        
        # Date
        date_ocr = self.extract_date_from_ocr()
        date_text = self.extract_date_from_text()
        fields['date'] = self.choose_best_match('date', date_ocr, date_text)
        
        return fields
    
    def extract_supplier_from_ocr(self) -> InvoiceField:
        """Extract supplier using OCR positional data"""
        # Look for company indicators near "FACTUUR"
        factuur_positions = self.find_word_positions('factuur')
        
        if factuur_positions:
            # Find words near FACTUUR with company indicators
            for page_data in self.ocr_data:
                for word in page_data['words']:
                    if re.search(r'(B\.V\.|BV|N\.V\.|NV|Holding|Group)', word.text, re.I):
                        # Check if it's reasonably close to FACTUUR
                        for factuur_pos in factuur_positions:
                            y_distance = abs(word.bbox.top - factuur_pos.bbox.top)
                            if y_distance < 200:  # Within 200 pixels
                                return InvoiceField(
                                    value=word.text,
                                    bbox=word.bbox,
                                    confidence=word.bbox.confidence,
                                    source='ocr'
                                )
        
        return InvoiceField('', None, 0.0, 'ocr')
    
    def extract_supplier_from_text(self) -> InvoiceField:
        """Extract supplier from plain text"""
        patterns = [
            r'FACTUUR\s*\n([^\n]+)',
            r'([A-Z][a-zA-Z\s]+(?:B\.V\.|BV|N\.V\.|NV))'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.extracted_text, re.I | re.M)
            if match and match.group(1).strip():
                return InvoiceField(
                    value=match.group(1).strip(),
                    bbox=None,
                    confidence=0.8,
                    source='text'
                )
        
        return InvoiceField('', None, 0.0, 'text')
    
    def extract_invoice_number_from_ocr(self) -> InvoiceField:
        """Extract invoice number using OCR coordinates"""
        # Look for V followed by digits
        for page_data in self.ocr_data:
            for word in page_data['words']:
                if re.match(r'V\d{6,}', word.text):
                    return InvoiceField(
                        value=word.text,
                        bbox=word.bbox,
                        confidence=word.bbox.confidence,
                        source='ocr'
                    )
        
        return InvoiceField('', None, 0.0, 'ocr')
    
    def extract_invoice_number_from_text(self) -> InvoiceField:
        """Extract invoice number from plain text"""
        patterns = [
            r'\b(V\d{6,})\b',
            r'(?:Factuurnummer|Invoice.*Number)\s*:?\s*([V]?\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.extracted_text, re.I)
            if match:
                return InvoiceField(
                    value=match.group(1),
                    bbox=None,
                    confidence=0.9,
                    source='text'
                )
        
        return InvoiceField('', None, 0.0, 'text')
    
    def extract_date_from_ocr(self) -> InvoiceField:
        """Extract date using OCR"""
        date_pattern = r'\d{1,2}[-\/]\d{1,2}[-\/]\d{4}'
        
        for page_data in self.ocr_data:
            for word in page_data['words']:
                if re.match(date_pattern, word.text):
                    normalized_date = self.normalize_date(word.text)
                    return InvoiceField(
                        value=normalized_date,
                        bbox=word.bbox,
                        confidence=word.bbox.confidence,
                        source='ocr'
                    )
        
        return InvoiceField('', None, 0.0, 'ocr')
    
    def extract_date_from_text(self) -> InvoiceField:
        """Extract date from plain text"""
        patterns = [
            r'(\d{1,2}[-\/]\d{1,2}[-\/]\d{4})',
            r'(?:Datum|Date):\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.extracted_text)
            if match:
                normalized_date = self.normalize_date(match.group(1))
                return InvoiceField(
                    value=normalized_date,
                    bbox=None,
                    confidence=0.8,
                    source='text'
                )
        
        return InvoiceField('', None, 0.0, 'text')
    
    def choose_best_match(self, field_type: str, ocr_result: InvoiceField, text_result: InvoiceField) -> InvoiceField:
        """Choose the best result between OCR and text extraction"""
        
        # If both found same value, prefer OCR (has position data)
        if ocr_result.value and text_result.value and ocr_result.value == text_result.value:
            return InvoiceField(
                value=ocr_result.value,
                bbox=ocr_result.bbox,
                confidence=max(ocr_result.confidence, text_result.confidence),
                source='hybrid'
            )
        
        # If only one found something, use that
        if ocr_result.value and not text_result.value:
            return ocr_result
        elif text_result.value and not ocr_result.value:
            return text_result
        
        # If both found different values, prefer higher confidence
        if ocr_result.confidence > text_result.confidence:
            return ocr_result
        else:
            return text_result
    
    def extract_line_items_with_positions(self) -> List[Dict]:
        """Extract line items using position-aware parsing"""
        items = []
        
        # Find table structure using OCR coordinates
        table_area = self.identify_table_area()
        
        if table_area:
            items = self.extract_from_table_area(table_area)
        
        # Fallback to text-based extraction
        if not items:
            items = self.extract_line_items_from_text()
        
        return items
    
    def identify_table_area(self) -> Optional[Dict]:
        """Identify the invoice line items table area"""
        # Look for "Omschrijving" or "Description" header
        header_positions = []
        header_positions.extend(self.find_word_positions('omschrijving'))
        header_positions.extend(self.find_word_positions('description'))
        
        if not header_positions:
            return None
        
        # Find the table boundaries
        header_pos = header_positions[0]
        
        # Look for currency symbols to define right boundary
        currency_positions = []
        for page_data in self.ocr_data:
            for word in page_data['words']:
                if '€' in word.text:
                    currency_positions.append(word)
        
        if currency_positions:
            rightmost_currency = max(currency_positions, key=lambda w: w.bbox.left + w.bbox.width)
            
            return {
                'top': header_pos.bbox.top,
                'left': header_pos.bbox.left,
                'right': rightmost_currency.bbox.left + rightmost_currency.bbox.width,
                'bottom': header_pos.bbox.top + 400  # Estimate table height
            }
        
        return None
    
    def extract_from_table_area(self, table_area: Dict) -> List[Dict]:
        """Extract line items from identified table area"""
        items = []
        
        # Group words by line within table area
        table_lines = {}
        
        for page_data in self.ocr_data:
            for word in page_data['words']:
                if (table_area['left'] <= word.bbox.left <= table_area['right'] and
                    table_area['top'] <= word.bbox.top <= table_area['bottom']):
                    
                    line_key = word.bbox.top // 20  # Group by approximate line (20px tolerance)
                    if line_key not in table_lines:
                        table_lines[line_key] = []
                    table_lines[line_key].append(word)
        
        # Process each line
        for line_key in sorted(table_lines.keys()):
            words = sorted(table_lines[line_key], key=lambda w: w.bbox.left)
            line_text = ' '.join([w.text for w in words])
            
            # Skip header lines
            if re.search(r'omschrijving|description|bedrag|amount', line_text, re.I):
                continue
                
            # Extract item data from positioned words
            item = self.parse_table_line(words, line_text)
            if item:
                items.append(item)
        
        return items
    
    def parse_table_line(self, words: List[WordData], line_text: str) -> Optional[Dict]:
        """Parse a table line using word positions"""
        if not words:
            return None
        
        # Find currency amounts
        amounts = []
        description_words = []
        
        for word in words:
            if '€' in word.text or re.match(r'[\d,]+\.\d{2}', word.text):
                # Extract numeric value
                amount_match = re.search(r'([\d,]+\.\d{2})', word.text)
                if amount_match:
                    amounts.append({
                        'value': float(amount_match.group(1).replace(',', '')),
                        'position': word.bbox.left,
                        'word': word
                    })
            else:
                description_words.append(word)
        
        if not amounts:
            return None
        
        # Build description from leftmost words
        description = ' '.join([w.text for w in description_words]).strip()
        
        if len(description) < 3:  # Minimum description length
            return None
        
        # Use rightmost amount as total
        total_amount = max(amounts, key=lambda a: a['position'])['value']
        
        return {
            'description': description,
            'quantity': 1,
            'rate': total_amount,
            'amount': total_amount,
            'confidence': 0.8,
            'source': 'ocr_positioned'
        }
    
    def extract_line_items_from_text(self) -> List[Dict]:
        """Fallback: Extract line items from plain text"""
        items = []
        lines = self.extracted_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for lines with currency amounts
            match = re.search(r'^(.+?)\s+€\s*([\d,]+\.\d{2})$', line)
            if match:
                description = match.group(1).strip()
                amount = float(match.group(2).replace(',', ''))
                
                # Skip total lines
                if re.search(r'totaal|total|btw|vat|subtotal', description, re.I):
                    continue
                
                if len(description) > 3:
                    items.append({
                        'description': description,
                        'quantity': 1,
                        'rate': amount,
                        'amount': amount,
                        'confidence': 0.6,
                        'source': 'text_fallback'
                    })
        
        return items
    
    def extract_totals_with_positions(self) -> Dict:
        """Extract totals using hybrid approach"""
        totals = {}
        
        # OCR-based total extraction
        total_words = []
        total_words.extend(self.find_word_positions('totaal'))
        total_words.extend(self.find_word_positions('total'))
        
        for total_word in total_words:
            # Look for amounts near "totaal" words
            for page_data in self.ocr_data:
                for word in page_data['words']:
                    if '€' in word.text:
                        y_distance = abs(word.bbox.top - total_word.bbox.top)
                        if y_distance < 30:  # Same line
                            amount_match = re.search(r'([\d,]+\.\d{2})', word.text)
                            if amount_match:
                                amount = float(amount_match.group(1).replace(',', ''))
                                
                                # Determine total type based on context
                                line_text = self.get_line_text_around_position(total_word.bbox)
                                if 'exclusief' in line_text.lower() or 'excl' in line_text.lower():
                                    totals['subtotal'] = amount
                                elif 'btw' in line_text.lower() or 'vat' in line_text.lower():
                                    totals['vat_amount'] = amount
                                elif 'betalen' in line_text.lower() or 'incl' in line_text.lower():
                                    totals['total'] = amount
        
        # Text-based fallback
        if not totals:
            text_totals = self.extract_totals_from_text()
            totals.update(text_totals)
        
        return totals
    
    def get_line_text_around_position(self, bbox: BoundingBox) -> str:
        """Get full line text around a position"""
        line_words = []
        
        for page_data in self.ocr_data:
            for word in page_data['words']:
                y_distance = abs(word.bbox.top - bbox.top)
                if y_distance < 20:  # Same line tolerance
                    line_words.append((word.bbox.left, word.text))
        
        # Sort by x position and join
        line_words.sort(key=lambda x: x[0])
        return ' '.join([w[1] for w in line_words])
    
    def extract_totals_from_text(self) -> Dict:
        """Extract totals from plain text"""
        totals = {}
        
        patterns = [
            (r'(?:Totaal exclusief.*btw).*€\s*([\d,]+\.\d{2})', 'subtotal'),
            (r'(?:Btw|VAT).*21%.*€\s*([\d,]+\.\d{2})', 'vat_amount'),
            (r'(?:Totaal te betalen|Total to pay).*€\s*([\d,]+\.\d{2})', 'total')
        ]
        
        for pattern, key in patterns:
            match = re.search(pattern, self.extracted_text, re.I)
            if match:
                totals[key] = float(match.group(1).replace(',', ''))
        
        return totals
    
    def normalize_date(self, date_str: str) -> str:
        """Convert date to YYYY-MM-DD format"""
        parts = re.split(r'[-\/]', date_str)
        if len(parts) == 3:
            if len(parts[0]) == 4:  # YYYY-MM-DD
                return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
            else:  # DD-MM-YYYY
                return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
        return date_str
    
    def calculate_overall_ocr_confidence(self) -> float:
        """Calculate average OCR confidence"""
        if not self.ocr_data:
            return 0.0
        
        total_confidence = 0
        word_count = 0
        
        for page_data in self.ocr_data:
            for word in page_data['words']:
                total_confidence += word.bbox.confidence
                word_count += 1
        
        return total_confidence / word_count if word_count > 0 else 0.0
    
    def calculate_hybrid_confidence(self, fields: Dict, line_items: List) -> float:
        """Calculate overall processing confidence"""
        field_confidence = sum([f.confidence for f in fields.values()]) / len(fields) if fields else 0
        
        item_confidence = 0
        if line_items:
            item_confidence = sum([item.get('confidence', 0) for item in line_items]) / len(line_items)
        
        ocr_confidence = self.calculate_overall_ocr_confidence()
        text_available = 0.2 if self.extracted_text.strip() else 0
        
        return min((field_confidence * 0.4 + item_confidence * 0.3 + ocr_confidence * 0.2 + text_available), 1.0)
    
    def fallback_to_text_only(self) -> Dict:
        """Fallback to text-only processing if OCR fails"""
        logger.warning("Falling back to text-only processing")
        
        # Simple text extraction
        supplier_match = re.search(r'FACTUUR\s*\n([^\n]+)', self.extracted_text, re.I)
        supplier = supplier_match.group(1).strip() if supplier_match else ''
        
        invoice_match = re.search(r'\b(V\d{6,})\b', self.extracted_text)
        invoice_number = invoice_match.group(1) if invoice_match else ''
        
        date_match = re.search(r'(\d{1,2}[-\/]\d{1,2}[-\/]\d{4})', self.extracted_text)
        date = self.normalize_date(date_match.group(1)) if date_match else ''
        
        return {
            "extracted_data": {
                "supplier_name": supplier,
                "invoice_number": invoice_number,
                "invoice_date": date,
                "currency": "EUR",
                "line_items": [],
                "totals": {}
            },
            "processing_info": {
                "ocr_confidence": 0.0,
                "text_extraction_available": bool(self.extracted_text.strip()),
                "hybrid_processing": False,
                "fallback_mode": True
            },
            "confidence_score": 0.3,
            "field_sources": {}
        }

def main():
    """Main function for command line usage"""
    if len(sys.argv) != 4:
        print("Usage: python hybrid_invoice_processor.py <pdf_path> <extracted_text> <output_json_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    extracted_text = sys.argv[2]
    output_path = sys.argv[3]
    
    # Process the invoice
    processor = HybridInvoiceProcessor(pdf_path, extracted_text)
    result = processor.process_invoice()
    
    # Save result
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Processing complete. Results saved to {output_path}")
    return result

if __name__ == "__main__":
    main()
