import re
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ReceiptItem:
    """Represents a single item on a receipt"""
    name: str
    quantity: float = 1.0
    price: float = 0.0
    category: str = "Uncategorized"

class DataParser:
    """Parses OCR text into structured receipt data"""
    
    def __init__(self):
        # Common receipt patterns
        self.price_pattern = r'\$?\s*(\d+\.?\d{2})'
        self.quantity_pattern = r'(\d+)\s*x\s*'
        
        # Common item name patterns to filter out
        self.ignore_patterns = [
            r'total', r'subtotal', r'tax', r'balance', r'due',
            r'change', r'cash', r'card', r'visa', r'mastercard',
            r'amex', r'receipt', r'thank you', r'store', r'address',
            r'phone', r'date', r'time', r'cashier', r'register'
        ]
    
    def parse(self, ocr_text: str) -> List[ReceiptItem]:
        """
        Parse OCR text into structured receipt items
        
        Strategy:
        1. Split text into lines
        2. Identify lines containing prices
        3. Extract item names, quantities, and prices
        4. Clean and validate data
        """
        lines = ocr_text.strip().split('\n')
        items = []
        
        for line in lines:
            # Skip if line contains ignored patterns
            if self._should_ignore(line):
                continue
            
            # Try to extract price
            price_match = re.findall(self.price_pattern, line)
            if not price_match:
                continue
            
            # Get the last price in line (usually the total for that item)
            price = float(price_match[-1])
            
            # Skip if price is suspicious (too high/low for a single item)
            if price > 1000 or price < 0.01:
                continue
            
            # Try to extract quantity
            quantity_match = re.search(self.quantity_pattern, line)
            quantity = 1.0
            if quantity_match:
                quantity = float(quantity_match.group(1))
            
            # Extract item name (remove price and quantity)
            item_name = self._extract_item_name(line, price, quantity)
            
            if item_name and len(item_name) > 2:  # Valid item name
                items.append(ReceiptItem(
                    name=item_name,
                    quantity=quantity,
                    price=price
                ))
        
        logger.info(f"Parsed {len(items)} items from receipt")
        return items
    
    def _should_ignore(self, line: str) -> bool:
        """Check if line should be ignored"""
        line_lower = line.lower()
        return any(re.search(pattern, line_lower) for pattern in self.ignore_patterns)
    
    def _extract_item_name(self, line: str, price: float, quantity: float) -> str:
        """Extract clean item name from line"""
        # Remove price
        line = re.sub(self.price_pattern, '', line)
        
        # Remove quantity pattern
        line = re.sub(self.quantity_pattern, '', line)
        
        # Remove special characters and extra spaces
        line = re.sub(r'[^\w\s\-\.]', ' ', line)
        line = re.sub(r'\s+', ' ', line).strip()
        
        return line.title()
    
    def calculate_total(self, items: List[ReceiptItem]) -> float:
        """Calculate total from items"""

        return sum(item.price for item in items)
