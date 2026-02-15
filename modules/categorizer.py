from typing import Dict, List
from modules.data_parser import ReceiptItem
import logging

logger = logging.getLogger(__name__)

class ExpenseCategorizer:
    """Categorizes receipt items into expense categories"""
    
    def __init__(self):
        # Define category keywords
        self.categories = {
            'Groceries': {
                'keywords': ['grocery', 'supermarket', 'food', 'mart', 'market'],
                'subcategories': {
                    'Dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'eggs'],
                    'Meat': ['chicken', 'beef', 'pork', 'fish', 'meat', 'seafood'],
                    'Produce': ['apple', 'banana', 'orange', 'vegetable', 'fruit', 'lettuce', 'tomato'],
                    'Bakery': ['bread', 'cake', 'muffin', 'donut', 'pastry', 'bagel'],
                    'Beverages': ['water', 'soda', 'juice', 'coffee', 'tea', 'drink'],
                    'Snacks': ['chip', 'candy', 'chocolate', 'cookie', 'snack', 'cracker'],
                    'Frozen': ['frozen', 'ice cream', 'pizza'],
                    'Pantry': ['rice', 'pasta', 'cereal', 'sauce', 'can', 'oil']
                }
            },
            'Dining': {
                'keywords': ['restaurant', 'cafe', 'starbucks', 'mcdonald', 'pizza hut', 'kfc'],
                'subcategories': {
                    'Fast Food': ['burger', 'fries', 'mcdonald', 'kfc', 'wendy'],
                    'Restaurant': ['dinner', 'lunch', 'breakfast', 'restaurant'],
                    'Coffee Shop': ['starbucks', 'coffee', 'cafe']
                }
            },
            'Shopping': {
                'keywords': ['walmart', 'target', 'costco', 'amazon', 'mall', 'store'],
                'subcategories': {
                    'Clothing': ['shirt', 'pant', 'jean', 'dress', 'shoe'],
                    'Electronics': ['phone', 'charger', 'cable', 'battery'],
                    'Household': ['cleaning', 'towel', 'paper', 'soap']
                }
            },
            'Transportation': {
                'keywords': ['gas', 'uber', 'lyft', 'taxi', 'transit', 'metro', 'bus'],
                'subcategories': {
                    'Fuel': ['gas', 'petrol'],
                    'Rideshare': ['uber', 'lyft', 'taxi'],
                    'Public Transit': ['bus', 'metro', 'train']
                }
            },
            'Healthcare': {
                'keywords': ['pharmacy', 'cvs', 'walgreens', 'medical', 'doctor'],
                'subcategories': {
                    'Pharmacy': ['medicine', 'pill', 'vitamin'],
                    'Medical': ['doctor', 'clinic', 'hospital']
                }
            }
        }
    
    def categorize(self, items: List[ReceiptItem]) -> Dict[str, List[ReceiptItem]]:
        """
        Categorize all items
        
        Returns:
            Dictionary with categories as keys and lists of items as values
        """
        categorized = {}
        
        for item in items:
            category, subcategory = self._get_category(item.name)
            
            # Create full category path
            full_category = f"{category} > {subcategory}" if subcategory else category
            
            if full_category not in categorized:
                categorized[full_category] = []
            
            item.category = full_category
            categorized[full_category].append(item)
        
        logger.info(f"Categorized items into {len(categorized)} categories")
        return categorized
    
    def _get_category(self, item_name: str) -> tuple:
        """Determine category and subcategory for an item"""
        item_lower = item_name.lower()
        
        for main_category, category_data in self.categories.items():
            # Check if item matches main category
            if any(keyword in item_lower for keyword in category_data['keywords']):
                # Check subcategories
                for subcat, keywords in category_data.get('subcategories', {}).items():
                    if any(keyword in item_lower for keyword in keywords):
                        return main_category, subcat
                return main_category, None
            
            # Check subcategories directly
            for subcat, keywords in category_data.get('subcategories', {}).items():
                if any(keyword in item_lower for keyword in keywords):
                    return main_category, subcat
        
        return "Other", None
    
    def calculate_category_totals(self, categorized: Dict[str, List[ReceiptItem]]) -> Dict[str, float]:
        """Calculate total spending per category"""
        totals = {}
        for category, items in categorized.items():
            totals[category] = sum(item.price for item in items)

        return totals
