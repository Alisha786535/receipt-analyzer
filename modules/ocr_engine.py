import pytesseract
import easyocr
import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class OCREngine:
    """Handles text extraction from receipt images"""
    
    def __init__(self, use_easyocr=True):
        self.use_easyocr = use_easyocr
        
        if use_easyocr:
            # Initialize EasyOCR with English language
            self.reader = easyocr.Reader(['en'], gpu=False)
            logger.info("EasyOCR initialized")
        else:
            # Configure Tesseract path if needed (Windows)
            # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            logger.info("Tesseract OCR initialized")
    
    def extract_text(self, image) -> str:
        """
        Extract text from preprocessed image
        
        Args:
            image: Preprocessed image (numpy array)
        
        Returns:
            Extracted text as string
        """
        try:
            if self.use_easyocr:
                result = self.reader.readtext(image, detail=0, paragraph=True)
                text = ' '.join(result)
            else:
                # Use Tesseract with receipt-specific configuration
                custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.$/% '
                text = pytesseract.image_to_string(image, config=custom_config)
            
            # Clean up text
            text = self._clean_text(text)
            logger.info(f"Extracted {len(text)} characters from image")
            
            return text
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Basic text cleaning"""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove empty lines
        text = '\n'.join([line.strip() for line in text.split('\n') if line.strip()])
        return text