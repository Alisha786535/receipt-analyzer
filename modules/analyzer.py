from typing import Dict, List, Tuple
from modules.data_parser import ReceiptItem
import numpy as np
import logging

logger = logging.getLogger(__name__)

class SpendingAnalyzer:
    """Analyzes spending patterns and identifies anomalies"""
    
    def __init__(self):
        # Define spending thresholds and typical patterns
        self.category_thresholds = {
            'Groceries': 200,
            'Dining': 100,
            'Shopping': 150,
            'Transportation': 100,
            'Healthcare': 100,
            'Other': 50
        }
    
    def calculate_percentages(self, category_totals: Dict[str, float], total: float) -> Dict[str, float]:
        """Calculate percentage of total spending per category"""
        if total == 0:
            return {}
        
        percentages = {}
        for category, amount in category_totals.items():
            percentages[category] = (amount / total) * 100
        
        logger.info("Calculated spending percentages")
        return percentages
    
    def identify_anomalies(self, category_totals: Dict[str, float]) -> List[Dict]:
        """
        Identify overspending areas or anomalies
        
        Returns:
            List of anomalies with category, amount, threshold, and severity
        """
        anomalies = []
        
        for category, amount in category_totals.items():
            # Extract main category from full path (e.g., "Groceries > Dairy" -> "Groceries")
            main_category = category.split(' > ')[0]
            
            # Check if category exceeds threshold
            threshold = self.category_thresholds.get(main_category, 50)
            
            if amount > threshold:
                anomalies.append({
                    'category': category,
                    'amount': amount,
                    'threshold': threshold,
                    'excess': amount - threshold,
                    'severity': 'High' if amount > threshold * 1.5 else 'Medium'
                })
        
        logger.info(f"Identified {len(anomalies)} anomalies")
        return anomalies
    
    def generate_summary_stats(self, items: List[ReceiptItem], categorized: Dict) -> Dict:
        """Generate comprehensive spending statistics"""
        
        # Basic stats
        total_items = len(items)
        total_spent = sum(item.price for item in items)
        avg_item_price = total_spent / total_items if total_items > 0 else 0
        
        # Find most expensive item
        if items:
            most_expensive = max(items, key=lambda x: x.price)
        else:
            most_expensive = None
        
        # Category with highest spending
        category_totals = self.calculate_category_totals(categorized)
        if category_totals:
            top_category = max(category_totals, key=category_totals.get)
            top_category_amount = category_totals[top_category]
        else:
            top_category = None
            top_category_amount = 0
        
        return {
            'total_items': total_items,
            'total_spent': round(total_spent, 2),
            'avg_item_price': round(avg_item_price, 2),
            'most_expensive_item': {
                'name': most_expensive.name if most_expensive else None,
                'price': most_expensive.price if most_expensive else 0
            },
            'top_category': {
                'name': top_category,
                'amount': round(top_category_amount, 2)
            },
            'category_count': len(category_totals)
        }
    
    def calculate_category_totals(self, categorized: Dict) -> Dict[str, float]:
        """Helper to calculate totals per category"""
        totals = {}
        for category, items in categorized.items():
            totals[category] = sum(item.price for item in items)

        return totals
