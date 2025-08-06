from openai import OpenAI
from flask import current_app
import json
from typing import Dict, List, Tuple

class BudgetTipGenerator:
    # Budget level thresholds
    BUDGET_LEVELS = {
        'low': 500.00,    # Under 500/day
        'medium': 1000.00 # 500-1000/day
        # Over 1000/day is considered 'high'
    }
    
    def __init__(self):
        """Initialize the OpenAI client with Groq configuration"""
        api_key = current_app.config.get('GROQ_API_KEY')
        if not api_key:
            current_app.logger.error("Groq API key not found in app config")
            raise ValueError("Groq API key not configured")

        current_app.logger.info("Initializing Groq client...")
        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            current_app.logger.info("Groq client initialized successfully")
        except Exception as e:
            current_app.logger.error(f"Failed to initialize Groq client: {str(e)}")
            raise

    def _validate_budget(self, daily_budget: float, monthly_budget: float) -> None:
        """Validate budget inputs"""
        if not isinstance(daily_budget, (int, float)) or not isinstance(monthly_budget, (int, float)):
            current_app.logger.error(f"Invalid budget types: daily={type(daily_budget)}, monthly={type(monthly_budget)}")
            raise TypeError("Budget values must be numbers")

        if daily_budget < 0 or monthly_budget < 0:
            current_app.logger.error(f"Negative budget values: daily={daily_budget}, monthly={monthly_budget}")
            raise ValueError("Budget values cannot be negative")

    def _determine_budget_level(self, daily_budget: float) -> str:
        """Determine the budget level (low, medium, high) based on daily amount"""
        if daily_budget < self.BUDGET_LEVELS['low']:
            return 'low'
        elif daily_budget < self.BUDGET_LEVELS['medium']:
            return 'medium'
        return 'high'

    def _get_allocations(self, daily_budget: float) -> Dict[str, float]:
        """Step 1: Get budget category allocations as percentages"""
        budget_level = self._determine_budget_level(daily_budget)
        
        prompt = f"""As a financial advisor, analyze this budget and return ONLY a JSON object containing recommended percentage allocations.
        Daily budget: PHP {daily_budget:.2f}
        Budget level: {budget_level}
        
        Rules:
        - Total must equal 100
        - Categories must include: Food, Transportation, Utilities, Emergency Fund, Discretionary
        - For {budget_level} budgets, follow these guidelines:
          low: Essentials 70-80%, Emergency 10-15%, Rest discretionary
          medium: Essentials 60-70%, Emergency 15-20%, Rest discretionary
          high: Essentials 50-60%, Emergency 20-25%, Rest discretionary/investments
        
        Return ONLY a JSON object like:
        {{"Food": 30, "Transportation": 20, "Utilities": 20, "Emergency Fund": 20, "Discretionary": 10}}"""

        try:
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial allocation expert. Respond only with a valid JSON object containing percentage allocations that sum to 100."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,  # Lower temperature for more consistent numerical output
                max_tokens=200    # Much shorter response needed
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise ValueError("No response from allocation API")
                
            # Parse and validate JSON response
            allocations = json.loads(response.choices[0].message.content)
            if not isinstance(allocations, dict) or sum(allocations.values()) != 100:
                raise ValueError("Invalid allocation response")
                
            return allocations
            
        except Exception as e:
            current_app.logger.error(f"Error getting allocations: {str(e)}")
            # Fallback to default allocations based on budget level
            if budget_level == 'low':
                return {"Food": 40, "Transportation": 20, "Utilities": 15, "Emergency Fund": 15, "Discretionary": 10}
            elif budget_level == 'medium':
                return {"Food": 35, "Transportation": 15, "Utilities": 15, "Emergency Fund": 20, "Discretionary": 15}
            return {"Food": 30, "Transportation": 15, "Utilities": 15, "Emergency Fund": 25, "Discretionary": 15}

    def generate_tip(self, daily_budget: float, monthly_budget: float) -> str:
        """Generate a complete budget breakdown and tips"""
        self._validate_budget(daily_budget, monthly_budget)

        try:
            # Step 1: Get budget allocations
            allocations = self._get_allocations(daily_budget)
            current_app.logger.info(f"Generated allocations: {allocations}")

            # Step 2: Calculate actual amounts
            breakdown = self._calculate_breakdown(daily_budget, allocations)
            current_app.logger.info(f"Calculated breakdown: {breakdown}")

            # Step 3: Get personalized tips
            tips = self._get_saving_tips(daily_budget, breakdown)
            current_app.logger.info(f"Generated tips: {tips}")

            # Step 4: Format final response
            response = self._format_response(daily_budget, monthly_budget, breakdown, tips)
            current_app.logger.info("Successfully generated budget advice")
            return response

        except Exception as e:
            current_app.logger.error(f"Error generating budget advice: {str(e)}")
            current_app.logger.error(f"Full error details: {repr(e)}")
            raise

    def _calculate_breakdown(self, daily_budget: float, allocations: Dict[str, float]) -> Dict[str, float]:
        """Calculate actual PHP amounts for each category"""
        return {
            category: (percentage / 100.0) * daily_budget
            for category, percentage in allocations.items()
        }

    def _get_saving_tips(self, daily_budget: float, breakdown: Dict[str, float]) -> List[Dict[str, str]]:
        """Step 3: Get personalized money-saving tips"""
        prompt = f"""Give 3 practical money-saving tips for someone in the Philippines with:
Daily budget: PHP {daily_budget:.2f}
Spending breakdown:
{json.dumps(breakdown, indent=2)}

Return ONLY a JSON array of 3 objects, each with:
- title: The tip title
- action: One specific, actionable step
- savings: Expected savings range in PHP (X.XX-Y.YY format)

Example:
[
  {{
    "title": "Smart Grocery Shopping",
    "action": "Buy fresh produce from wet markets early morning",
    "savings": "50.00-100.00"
  }}
]"""

        try:
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a local financial advisor in the Philippines. Return only valid JSON arrays of money-saving tips."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,  # More creative for tips
                max_tokens=500
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise ValueError("No response from tips API")
                
            tips = json.loads(response.choices[0].message.content)
            if not isinstance(tips, list) or len(tips) != 3:
                raise ValueError("Invalid tips format")
                
            return tips
            
        except Exception as e:
            current_app.logger.error(f"Error getting tips: {str(e)}")
            # Fallback to generic tips
            return [
                {
                    "title": "Smart Grocery Shopping",
                    "action": "Buy fresh produce from local markets early morning",
                    "savings": "50.00-100.00"
                },
                {
                    "title": "Transportation Planning",
                    "action": "Use public transport during off-peak hours",
                    "savings": "20.00-50.00"
                },
                {
                    "title": "Utility Savings",
                    "action": "Use natural lighting and ventilation when possible",
                    "savings": "100.00-200.00"
                }
            ]

    def _format_response(self, daily_budget: float, monthly_budget: float, 
                        breakdown: Dict[str, float], tips: List[Dict[str, str]]) -> str:
        """Format the final response with proper structure and formatting"""
        # Calculate totals
        essential_categories = ['Food', 'Transportation', 'Utilities']
        essentials_total = sum(breakdown[cat] for cat in essential_categories if cat in breakdown)
        
        # Sort the breakdown items to show essentials first
        sorted_items = []
        
        # First add essential categories
        for cat in ['Food', 'Transportation', 'Utilities']:
            if cat in breakdown:
                sorted_items.append((cat, breakdown[cat]))
                
        # Then add totals and emergency/discretionary funds
        response = [
            "Daily Budget Summary:",
            f"PHP {daily_budget:.2f}",
            "",
            "Budget Breakdown:",
            *[f"{cat}: PHP {amount:.2f}" for cat, amount in sorted_items],
            f"Total Essential Expenses: PHP {essentials_total:.2f}",
            "",
            "Savings and Discretionary:",
            f"Emergency Fund: PHP {breakdown.get('Emergency Fund', 0):.2f}",
            f"Discretionary: PHP {breakdown.get('Discretionary', 0):.2f}",
            "",
            "Money-Saving Tips:"
        ]
        
        # Add formatted tips with consistent bullet points and indentation
        for i, tip in enumerate(tips, 1):
            response.extend([
                f"{i}. {tip['title']}",
                f"• {tip['action']}",
                f"• Expected savings: PHP {tip['savings']}",
                ""  # Add blank line between tips
            ])
        
        # Remove the last empty line if it exists
        if response[-1] == "":
            response.pop()
            
        return "\n".join(response)