import google.generativeai as genai
from typing import Dict, List
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class LLMAdvisor:
    """Generates personalized financial advice using LLM"""
    
    def __init__(self, api_key=None):
        """Initialize LLM (Gemini or fallback to rule-based advice)"""
        self.use_llm = False
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.use_llm = True
                logger.info("LLM initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM: {str(e)}")
    
    def generate_advice(self, summary_stats: Dict, anomalies: List[Dict], 
                        percentages: Dict[str, float]) -> Dict[str, str]:
        """
        Generate personalized financial advice
        
        Returns:
            Dictionary with different types of advice
        """
        if self.use_llm:
            return self._generate_llm_advice(summary_stats, anomalies, percentages)
        else:
            return self._generate_rule_based_advice(summary_stats, anomalies, percentages)
    
    def _generate_llm_advice(self, summary_stats, anomalies, percentages):
        """Generate advice using Gemini LLM"""
        
        # Prepare context for LLM
        context = f"""
        Spending Analysis Summary:
        - Total spent: ${summary_stats['total_spent']}
        - Number of items: {summary_stats['total_items']}
        - Average item price: ${summary_stats['avg_item_price']}
        - Top spending category: {summary_stats['top_category']['name']} (${summary_stats['top_category']['amount']})
        
        Spending by Category:
        {self._format_percentages(percentages)}
        
        Areas of Concern:
        {self._format_anomalies(anomalies)}
        
        Based on this spending data, provide:
        1. Three specific money-saving tips tailored to this spending pattern
        2. One actionable budgeting recommendation
        3. A positive observation about their spending habits
        """
        
        try:
            response = self.model.generate_content(context)
            return {
                'advice': response.text,
                'source': 'Gemini AI'
            }
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            return self._generate_rule_based_advice(summary_stats, anomalies, percentages)
    
    def _generate_rule_based_advice(self, summary_stats, anomalies, percentages):
        """Generate rule-based advice when LLM is unavailable"""
        
        advice = []
        tips = []
        recommendations = []
        
        # Analyze spending patterns
        total = summary_stats['total_spent']
        
        # Check for anomalies
        if anomalies:
            advice.append("⚠️ **Overspending Alert**")
            for anomaly in anomalies:
                advice.append(f"- You spent ${anomaly['amount']:.2f} on {anomaly['category']}, "
                            f"which is ${anomaly['excess']:.2f} above typical budget")
        
        # Category-specific advice
        for category, percentage in percentages.items():
            main_cat = category.split(' > ')[0]
            
            if percentage > 30:
                advice.append(f"📊 {percentage:.1f}% of your spending is on {category}. "
                            "Consider if this aligns with your priorities.")
                
                if main_cat == 'Dining':
                    tips.append("Try meal prepping to reduce dining expenses")
                elif main_cat == 'Shopping':
                    tips.append("Implement a 24-hour waiting period for non-essential purchases")
                elif main_cat == 'Groceries':
                    tips.append("Plan meals and use shopping lists to avoid impulse buys")
        
        # Positive observations
        positive_notes = []
        if total < 100:
            positive_notes.append("Great job keeping total spending under $100!")
        
        if 'Healthcare' in str(percentages) and percentages.get('Healthcare', 0) > 0:
            positive_notes.append("Good to see you're investing in health and wellness")
        
        # Generate tips
        if not tips:
            tips = [
                "Track your expenses regularly to stay aware of spending patterns",
                "Look for subscription services you might have forgotten about",
                "Consider using cash envelopes for variable expenses"
            ]
        
        # Compile response
        return {
            'summary': '\n'.join(advice) if advice else "Your spending looks balanced!",
            'tips': tips[:3],
            'positive_notes': positive_notes if positive_notes else ["You're being mindful of your spending!"],
            'source': 'Rule-based System'
        }
    
    def _format_percentages(self, percentages):
        """Format percentages for LLM context"""
        return '\n'.join([f"- {cat}: {pct:.1f}%" for cat, pct in percentages.items()])
    
    def _format_anomalies(self, anomalies):
        """Format anomalies for LLM context"""
        if not anomalies:
            return "No significant anomalies detected"
        return '\n'.join([f"- {a['category']}: ${a['amount']:.2f} "
                          f"(exceeds threshold by ${a['excess']:.2f})" 
                          for a in anomalies])