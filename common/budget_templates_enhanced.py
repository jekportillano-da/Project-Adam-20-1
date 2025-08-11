"""
Enhanced Smart Budget Templates and Presets
Provides pre-configured budget templates with dynamic adjustments based on lifestyle factors
"""

from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
import math

class BudgetTemplates:
    """Smart budget templates with dynamic lifestyle-based adjustments"""
    
    @staticmethod
    def get_all_templates() -> Dict[str, Any]:
        """Get all available budget templates - these serve as baselines"""
        return {
            "fresh_graduate": {
                "name": "Fresh Graduate (₱18K-25K)",
                "description": "Starting career with focus on emergency fund building",
                "income_range": (18000, 25000),
                "allocations": {
                    "housing": 0.25,
                    "food": 0.25,
                    "transportation": 0.15,
                    "utilities": 0.10,
                    "emergency_fund": 0.15,
                    "discretionary": 0.07,
                    "investments": 0.03
                },
                "tips": [
                    "Focus on building emergency fund first",
                    "Consider shared housing to reduce costs",
                    "Use public transportation when possible",
                    "Start with small, consistent investments"
                ]
            },
            
            "young_professional": {
                "name": "Young Professional (₱25K-40K)",
                "description": "Career growth phase with balanced savings approach",
                "income_range": (25000, 40000),
                "allocations": {
                    "housing": 0.30,
                    "food": 0.22,
                    "transportation": 0.18,
                    "utilities": 0.08,
                    "emergency_fund": 0.12,
                    "discretionary": 0.06,
                    "investments": 0.04
                },
                "tips": [
                    "Prioritize building 6-month emergency fund",
                    "Invest in skills development courses",
                    "Start diversified investment portfolio",
                    "Consider life insurance"
                ]
            },
            
            "family_breadwinner": {
                "name": "Family Breadwinner (₱35K-60K)",
                "description": "Supporting family with emphasis on stability",
                "income_range": (35000, 60000),
                "allocations": {
                    "housing": 0.35,
                    "food": 0.30,
                    "transportation": 0.12,
                    "utilities": 0.12,
                    "emergency_fund": 0.08,
                    "discretionary": 0.02,
                    "investments": 0.01
                },
                "tips": [
                    "Maintain larger emergency fund for family security",
                    "Consider family health insurance",
                    "Plan for children's education fund",
                    "Focus on stable, low-risk investments"
                ]
            },
            
            "ofw_remittance": {
                "name": "OFW Remittance Manager (₱40K-80K)",
                "description": "Managing overseas income with higher savings capacity",
                "income_range": (40000, 80000),
                "allocations": {
                    "housing": 0.20,
                    "food": 0.20,
                    "transportation": 0.10,
                    "utilities": 0.08,
                    "emergency_fund": 0.20,
                    "discretionary": 0.12,
                    "investments": 0.10
                },
                "tips": [
                    "Build substantial emergency fund",
                    "Consider property investment back home",
                    "Diversify investments across countries",
                    "Plan for eventual return/retirement"
                ]
            },
            
            "senior_executive": {
                "name": "Senior Executive (₱60K-120K)",
                "description": "High earner focused on wealth building",
                "income_range": (60000, 120000),
                "allocations": {
                    "housing": 0.25,
                    "food": 0.15,
                    "transportation": 0.12,
                    "utilities": 0.08,
                    "emergency_fund": 0.15,
                    "discretionary": 0.10,
                    "investments": 0.15
                },
                "tips": [
                    "Maximize investment opportunities",
                    "Consider real estate investments",
                    "Optimize tax strategies",
                    "Plan for early retirement options"
                ]
            },
            
            "entrepreneur": {
                "name": "Entrepreneur (₱30K-150K+)",
                "description": "Variable income with higher risk tolerance",
                "income_range": (30000, 150000),
                "allocations": {
                    "housing": 0.25,
                    "food": 0.18,
                    "transportation": 0.12,
                    "utilities": 0.08,
                    "emergency_fund": 0.25,  # Higher due to income volatility
                    "discretionary": 0.07,
                    "investments": 0.05
                },
                "tips": [
                    "Build larger emergency fund for income volatility",
                    "Separate business and personal finances",
                    "Consider business insurance",
                    "Reinvest profits strategically"
                ]
            }
        }
    
    @staticmethod
    def recommend_template(income: float, lifestyle_factors: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, Any]]:
        """Recommend the best template based on income and lifestyle factors"""
        templates = BudgetTemplates.get_all_templates()
        
        # Default to income-based selection
        best_template_id = "young_professional"  # Default fallback
        
        for template_id, template in templates.items():
            income_range = template["income_range"]
            if income_range[0] <= income <= income_range[1]:
                best_template_id = template_id
                break
        
        # Adjust recommendation based on lifestyle factors
        if lifestyle_factors:
            # Family considerations
            if lifestyle_factors.get("has_kids", False) or lifestyle_factors.get("dependents", 0) > 0:
                if income >= 35000:
                    best_template_id = "family_breadwinner"
            
            # OFW considerations
            if lifestyle_factors.get("location") == "overseas" or lifestyle_factors.get("is_ofw", False):
                if income >= 40000:
                    best_template_id = "ofw_remittance"
            
            # Executive level
            if income >= 60000 and lifestyle_factors.get("job_level") == "executive":
                best_template_id = "senior_executive"
            
            # Entrepreneur
            if lifestyle_factors.get("income_type") == "business" or lifestyle_factors.get("is_entrepreneur", False):
                best_template_id = "entrepreneur"
        
        return best_template_id, templates[best_template_id]
    
    @staticmethod
    def generate_budget_from_template(template_id: str, income: float) -> Dict[str, float]:
        """Generate basic budget breakdown from template (original method preserved)"""
        templates = BudgetTemplates.get_all_templates()
        template = templates.get(template_id)
        
        if not template:
            raise ValueError(f"Template '{template_id}' not found")
        
        budget = {}
        allocations = template["allocations"]
        
        for category, percentage in allocations.items():
            budget[category] = income * percentage
        
        return budget
    
    @staticmethod
    def generate_dynamic_budget(template_id: str, income: float, lifestyle_factors: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate dynamically adjusted budget based on template baseline and lifestyle factors.
        
        Args:
            template_id: Base template to use
            income: Monthly income
            lifestyle_factors: Dictionary of lifestyle adjustments including:
                - rent_pct: Current rent as percentage of income (0-1)
                - has_kids: Boolean, affects food/utilities allocation
                - debt_ratio: Total debt payments as percentage of income (0-1)
                - car_payment: Monthly car payment amount
                - location: 'metro', 'urban', 'rural' affects costs
                - target_savings_rate: Desired total savings rate (0-1)
                - age: Age affects investment vs emergency focus
                - dependents: Number of dependents
                - is_ofw: Boolean, overseas worker considerations
                - job_level: 'entry', 'mid', 'senior', 'executive'
                - income_stability: 'stable', 'variable', 'seasonal'
        
        Returns:
            Dictionary with:
            - adjusted allocations (percentages and amounts)
            - financial health score
            - original template tips
            - adjustment rationale explaining changes made
        """
        templates = BudgetTemplates.get_all_templates()
        template = templates.get(template_id)
        
        if not template:
            raise ValueError(f"Template '{template_id}' not found")
        
        if lifestyle_factors is None:
            lifestyle_factors = {}
        
        # Start with template baseline
        base_allocations = template["allocations"].copy()
        
        # Apply dynamic adjustments with rationale tracking
        adjusted_allocations, adjustment_notes = BudgetTemplates._apply_lifestyle_adjustments(
            base_allocations, lifestyle_factors, income
        )
        
        # Normalize to ensure sum equals 1.0
        normalized_allocations = BudgetTemplates._normalize_allocations(adjusted_allocations)
        
        # Calculate peso amounts
        budget_amounts = {category: income * percentage for category, percentage in normalized_allocations.items()}
        
        # Calculate financial health score
        health_score = BudgetTemplates._calculate_health_score(budget_amounts, income)
        
        # Calculate total savings rate
        total_savings = budget_amounts.get("emergency_fund", 0) + budget_amounts.get("investments", 0)
        savings_rate = (total_savings / income) * 100 if income > 0 else 0
        
        # Prepare comprehensive result
        result = {
            "template_name": template["name"],
            "template_id": template_id,
            "income": income,
            "allocations_percentage": normalized_allocations,
            "allocations_amount": budget_amounts,
            "monthly_savings": total_savings,
            "savings_rate": savings_rate,
            "financial_health_score": health_score,
            "original_tips": template["tips"].copy(),
            "adjustment_rationale": adjustment_notes,
            "lifestyle_factors_applied": lifestyle_factors.copy(),
            "baseline_vs_adjusted": {
                category: {
                    "baseline": base_allocations.get(category, 0),
                    "adjusted": normalized_allocations.get(category, 0),
                    "change": normalized_allocations.get(category, 0) - base_allocations.get(category, 0)
                }
                for category in set(list(base_allocations.keys()) + list(normalized_allocations.keys()))
            }
        }
        
        return result
    
    @staticmethod
    def _apply_lifestyle_adjustments(allocations: Dict[str, float], factors: Dict[str, Any], income: float) -> Tuple[Dict[str, float], List[str]]:
        """
        Apply lifestyle factor adjustments to base allocations.
        This is the core logic engine that makes rule-based adjustments.
        """
        adjusted = allocations.copy()
        notes = []
        
        # Define category limits (min, max percentages) - these are guardrails
        limits = {
            "housing": (0.15, 0.50),        # Housing: 15-50%
            "food": (0.12, 0.40),           # Food: 12-40% 
            "transportation": (0.05, 0.25), # Transport: 5-25%
            "utilities": (0.04, 0.15),      # Utilities: 4-15%
            "emergency_fund": (0.05, 0.30), # Emergency: 5-30%
            "discretionary": (0.01, 0.20),  # Discretionary: 1-20%
            "investments": (0.00, 0.35)     # Investments: 0-35%
        }
        
        # 1. HOUSING COST ADJUSTMENT
        rent_pct = factors.get("rent_pct")
        if rent_pct is not None and 0 <= rent_pct <= 1:
            current_housing = adjusted.get("housing", 0.30)
            
            if rent_pct > current_housing + 0.03:  # Rent significantly higher than template
                adjustment = min(rent_pct - current_housing, 0.12)  # Cap increase at 12%
                adjusted["housing"] = min(current_housing + adjustment, limits["housing"][1])
                
                # Compensate by reducing discretionary and food proportionally
                reduction_needed = adjustment
                discretionary_reduction = min(reduction_needed * 0.6, adjusted.get("discretionary", 0.08) - limits["discretionary"][0])
                food_reduction = min(reduction_needed * 0.4, adjusted.get("food", 0.25) - limits["food"][0])
                
                adjusted["discretionary"] = adjusted.get("discretionary", 0.08) - discretionary_reduction
                adjusted["food"] = adjusted.get("food", 0.25) - food_reduction
                
                notes.append(f"Increased housing to {adjusted['housing']:.1%} due to higher actual rent ({rent_pct:.1%})")
                
            elif rent_pct < current_housing - 0.03:  # Rent significantly lower
                reduction = min(current_housing - rent_pct, 0.08)
                adjusted["housing"] = max(current_housing - reduction, limits["housing"][0])
                
                # Redirect savings to investments and emergency fund
                investment_boost = reduction * 0.6
                emergency_boost = reduction * 0.4
                
                adjusted["investments"] = min(adjusted.get("investments", 0.04) + investment_boost, limits["investments"][1])
                adjusted["emergency_fund"] = min(adjusted.get("emergency_fund", 0.10) + emergency_boost, limits["emergency_fund"][1])
                
                notes.append(f"Reduced housing to {adjusted['housing']:.1%}, increased savings due to lower rent")
        
        # 2. FAMILY WITH CHILDREN ADJUSTMENT
        has_kids = factors.get("has_kids", False)
        dependents = factors.get("dependents", 0)
        
        if has_kids or dependents > 0:
            # Increase food and utilities for family needs
            dependent_count = max(1 if has_kids else 0, dependents)
            food_increase = min(dependent_count * 0.03, 0.08)  # Max 8% increase
            utilities_increase = min(dependent_count * 0.02, 0.04)  # Max 4% increase
            
            adjusted["food"] = min(adjusted.get("food", 0.25) + food_increase, limits["food"][1])
            adjusted["utilities"] = min(adjusted.get("utilities", 0.08) + utilities_increase, limits["utilities"][1])
            
            # Reduce discretionary and investments to compensate
            total_increase = food_increase + utilities_increase
            discretionary_reduction = min(total_increase * 0.7, adjusted.get("discretionary", 0.08) - limits["discretionary"][0])
            investment_reduction = min(total_increase * 0.3, adjusted.get("investments", 0.04) - limits["investments"][0])
            
            adjusted["discretionary"] = adjusted.get("discretionary", 0.08) - discretionary_reduction
            adjusted["investments"] = adjusted.get("investments", 0.04) - investment_reduction
            
            family_type = "children" if has_kids else f"{dependents} dependent(s)"
            notes.append(f"Increased food ({food_increase:.1%}) and utilities ({utilities_increase:.1%}) for family with {family_type}")
        
        # 3. DEBT LOAD ADJUSTMENT
        debt_ratio = factors.get("debt_ratio", 0)
        if debt_ratio > 0.15:  # Significant debt load (>15% of income)
            # High debt requires larger emergency fund as safety net
            emergency_boost = min(debt_ratio * 0.3, 0.08)  # Scale with debt, max 8%
            adjusted["emergency_fund"] = min(adjusted.get("emergency_fund", 0.10) + emergency_boost, limits["emergency_fund"][1])
            
            # Reduce investments and discretionary spending
            investment_reduction = min(emergency_boost * 0.6, adjusted.get("investments", 0.04) - limits["investments"][0])
            discretionary_reduction = emergency_boost - investment_reduction
            
            adjusted["investments"] = adjusted.get("investments", 0.04) - investment_reduction
            adjusted["discretionary"] = max(adjusted.get("discretionary", 0.08) - discretionary_reduction, limits["discretionary"][0])
            
            notes.append(f"Increased emergency fund ({emergency_boost:.1%}) due to high debt load ({debt_ratio:.1%})")
        
        # 4. TRANSPORTATION COSTS (Car Payment)
        car_payment = factors.get("car_payment", 0)
        if car_payment > 0 and income > 0:
            car_pct = min(car_payment / income, 0.20)  # Cap at 20% of income
            current_transport = adjusted.get("transportation", 0.15)
            
            if car_pct > current_transport:
                transport_increase = min(car_pct - current_transport, 0.08)
                adjusted["transportation"] = min(current_transport + transport_increase, limits["transportation"][1])
                
                # Reduce discretionary to compensate
                adjusted["discretionary"] = max(adjusted.get("discretionary", 0.08) - transport_increase, limits["discretionary"][0])
                
                notes.append(f"Increased transportation ({transport_increase:.1%}) for car payment (₱{car_payment:,.0f})")
        
        # 5. LOCATION-BASED COST ADJUSTMENTS
        location = factors.get("location", "urban").lower()
        if location == "metro":
            # Metro areas: higher housing and transportation costs
            housing_boost = 0.03
            transport_boost = 0.02
            
            adjusted["housing"] = min(adjusted.get("housing", 0.30) + housing_boost, limits["housing"][1])
            adjusted["transportation"] = min(adjusted.get("transportation", 0.15) + transport_boost, limits["transportation"][1])
            
            # Reduce discretionary and food proportionally
            total_boost = housing_boost + transport_boost
            discretionary_reduction = min(total_boost * 0.6, adjusted.get("discretionary", 0.08) - limits["discretionary"][0])
            food_reduction = min(total_boost * 0.4, adjusted.get("food", 0.25) - limits["food"][0])
            
            adjusted["discretionary"] = adjusted.get("discretionary", 0.08) - discretionary_reduction
            adjusted["food"] = adjusted.get("food", 0.25) - food_reduction
            
            notes.append("Increased housing/transport allocations for metro area cost of living")
            
        elif location == "rural":
            # Rural areas: lower housing costs, potential transport needs
            housing_reduction = 0.04
            adjusted["housing"] = max(adjusted.get("housing", 0.30) - housing_reduction, limits["housing"][0])
            
            # Redirect housing savings to investments and emergency fund
            investment_boost = housing_reduction * 0.7
            emergency_boost = housing_reduction * 0.3
            
            adjusted["investments"] = min(adjusted.get("investments", 0.04) + investment_boost, limits["investments"][1])
            adjusted["emergency_fund"] = min(adjusted.get("emergency_fund", 0.10) + emergency_boost, limits["emergency_fund"][1])
            
            notes.append("Reduced housing costs for rural area, increased savings")
        
        # 6. TARGET SAVINGS RATE ADJUSTMENT
        target_savings_rate = factors.get("target_savings_rate")
        if target_savings_rate is not None and 0 <= target_savings_rate <= 0.5:  # Cap at 50%
            current_savings_rate = adjusted.get("emergency_fund", 0.10) + adjusted.get("investments", 0.04)
            
            if target_savings_rate > current_savings_rate + 0.02:  # Meaningful increase needed
                savings_increase = min(target_savings_rate - current_savings_rate, 0.15)  # Max 15% increase
                
                # Distribute between emergency fund and investments based on current levels and age
                age = factors.get("age", 30)
                current_emergency = adjusted.get("emergency_fund", 0.10)
                
                # Young people (under 35) lean more toward investments
                # Older people lean toward emergency fund
                if age < 35 and current_emergency >= 0.15:
                    investment_portion = 0.75  # 75% to investments
                elif age > 45:
                    investment_portion = 0.25  # 25% to investments
                else:
                    investment_portion = 0.5   # 50/50 split
                
                investment_increase = savings_increase * investment_portion
                emergency_increase = savings_increase * (1 - investment_portion)
                
                adjusted["investments"] = min(adjusted.get("investments", 0.04) + investment_increase, limits["investments"][1])
                adjusted["emergency_fund"] = min(adjusted.get("emergency_fund", 0.10) + emergency_increase, limits["emergency_fund"][1])
                
                # Reduce other categories to fund increased savings
                remaining_reduction = savings_increase
                categories_to_reduce = ["discretionary", "food", "transportation"]
                
                for category in categories_to_reduce:
                    if remaining_reduction <= 0:
                        break
                    
                    current_value = adjusted.get(category, 0)
                    min_value = limits[category][0]
                    max_reduction = current_value - min_value
                    
                    if max_reduction > 0:
                        reduction = min(remaining_reduction * 0.4, max_reduction)
                        adjusted[category] = current_value - reduction
                        remaining_reduction -= reduction
                
                notes.append(f"Adjusted savings rate to target {target_savings_rate:.1%} (emergency: +{emergency_increase:.1%}, investments: +{investment_increase:.1%})")
        
        # 7. AGE-BASED INVESTMENT STRATEGY
        age = factors.get("age")
        if age is not None:
            if age < 30:
                # Young: more aggressive investing, higher risk tolerance
                investment_boost = 0.02
                emergency_reduction = 0.01
                
                adjusted["investments"] = min(adjusted.get("investments", 0.04) + investment_boost, limits["investments"][1])
                adjusted["emergency_fund"] = max(adjusted.get("emergency_fund", 0.10) - emergency_reduction, limits["emergency_fund"][0])
                
                notes.append("Increased investment allocation for younger age group (higher growth potential)")
                
            elif age > 50:
                # Older: more conservative, higher emergency fund, lower risk
                emergency_boost = 0.03
                investment_reduction = 0.02
                
                adjusted["emergency_fund"] = min(adjusted.get("emergency_fund", 0.10) + emergency_boost, limits["emergency_fund"][1])
                adjusted["investments"] = max(adjusted.get("investments", 0.04) - investment_reduction, limits["investments"][0])
                
                notes.append("Increased emergency fund for older age group (stability focus)")
        
        # 8. INCOME STABILITY ADJUSTMENT
        income_stability = factors.get("income_stability", "stable").lower()
        if income_stability in ["variable", "seasonal"]:
            # Variable income requires larger emergency buffer
            emergency_boost = 0.05
            adjusted["emergency_fund"] = min(adjusted.get("emergency_fund", 0.10) + emergency_boost, limits["emergency_fund"][1])
            
            # Reduce investments slightly for more liquidity
            investment_reduction = 0.02
            adjusted["investments"] = max(adjusted.get("investments", 0.04) - investment_reduction, limits["investments"][0])
            
            # Reduce discretionary for remaining adjustment
            discretionary_reduction = emergency_boost - investment_reduction
            adjusted["discretionary"] = max(adjusted.get("discretionary", 0.08) - discretionary_reduction, limits["discretionary"][0])
            
            notes.append(f"Increased emergency fund due to {income_stability} income pattern")
        
        return adjusted, notes
    
    @staticmethod
    def _normalize_allocations(allocations: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize allocations to sum to exactly 1.0 while respecting category limits.
        """
        total = sum(allocations.values())
        
        if abs(total - 1.0) < 0.005:  # Already very close (within 0.5%)
            return allocations
        
        # Proportional scaling to reach exactly 1.0
        scaling_factor = 1.0 / total
        normalized = {category: percentage * scaling_factor for category, percentage in allocations.items()}
        
        return normalized
    
    @staticmethod
    def get_template_insights(template_id: str, income: float) -> Dict[str, Any]:
        """Get insights and recommendations for a specific template (preserved original method)"""
        templates = BudgetTemplates.get_all_templates()
        template = templates.get(template_id)
        
        if not template:
            return {}
        
        budget = BudgetTemplates.generate_budget_from_template(template_id, income)
        
        return {
            "template": template,
            "budget": budget,
            "monthly_savings": budget.get("emergency_fund", 0) + budget.get("investments", 0),
            "savings_rate": (budget.get("emergency_fund", 0) + budget.get("investments", 0)) / income * 100,
            "financial_health_score": BudgetTemplates._calculate_health_score(budget, income),
            "recommendations": template["tips"]
        }
    
    @staticmethod
    def _calculate_health_score(budget: Dict[str, float], income: float) -> float:
        """
        Calculate financial health score based on budget allocation.
        Enhanced with more comprehensive scoring criteria.
        """
        score = 100
        
        # Housing cost evaluation (weight: 25%)
        housing_ratio = budget.get("housing", 0) / income if income > 0 else 0
        if housing_ratio > 0.40:
            score -= (housing_ratio - 0.40) * 100  # Major penalty for very high housing
        elif housing_ratio > 0.30:
            score -= (housing_ratio - 0.30) * 50   # Moderate penalty
        elif housing_ratio < 0.15:
            score -= (0.15 - housing_ratio) * 30   # Small penalty for unrealistically low
        
        # Emergency fund evaluation (weight: 25%)
        emergency_ratio = budget.get("emergency_fund", 0) / income if income > 0 else 0
        if emergency_ratio >= 0.15:
            score += 15  # Bonus for good emergency fund
        elif emergency_ratio >= 0.10:
            score += 8   # Small bonus
        elif emergency_ratio < 0.05:
            score -= 20  # Penalty for insufficient emergency fund
        
        # Total savings rate evaluation (weight: 20%)
        total_savings = budget.get("emergency_fund", 0) + budget.get("investments", 0)
        savings_rate = total_savings / income if income > 0 else 0
        if savings_rate >= 0.25:
            score += 15  # Excellent savings rate
        elif savings_rate >= 0.15:
            score += 10  # Good savings rate
        elif savings_rate >= 0.10:
            score += 5   # Adequate savings rate
        elif savings_rate < 0.05:
            score -= 15  # Insufficient savings
        
        # Food cost evaluation (weight: 15%)
        food_ratio = budget.get("food", 0) / income if income > 0 else 0
        if food_ratio > 0.35:
            score -= (food_ratio - 0.35) * 80  # High food costs
        elif food_ratio < 0.10:
            score -= (0.10 - food_ratio) * 50  # Unrealistically low food budget
        
        # Transportation evaluation (weight: 10%)
        transport_ratio = budget.get("transportation", 0) / income if income > 0 else 0
        if transport_ratio > 0.20:
            score -= (transport_ratio - 0.20) * 60
        
        # Discretionary spending balance (weight: 5%)
        discretionary_ratio = budget.get("discretionary", 0) / income if income > 0 else 0
        if discretionary_ratio > 0.15:
            score -= (discretionary_ratio - 0.15) * 40  # Too much discretionary
        elif discretionary_ratio < 0.01:
            score -= 5  # Too restrictive, unsustainable
        
        # Ensure score stays within bounds
        return max(0, min(100, score))


# Example usage demonstrating the enhanced functionality
if __name__ == "__main__":
    # Example 1: Basic template recommendation
    income = 45000
    template_id, template = BudgetTemplates.recommend_template(income)
    print(f"Recommended template for ₱{income:,}: {template['name']}")
    
    # Example 2: Dynamic budget with lifestyle factors
    lifestyle_factors = {
        "rent_pct": 0.38,           # Paying 38% of income on rent (higher than template)
        "has_kids": True,           # Has children
        "debt_ratio": 0.12,         # 12% of income goes to debt payments
        "car_payment": 8000,        # ₱8,000 monthly car payment
        "location": "metro",        # Lives in metro area
        "target_savings_rate": 0.18, # Wants to save 18% of income
        "age": 32,                  # 32 years old
        "dependents": 2             # 2 dependents
    }
    
    dynamic_budget = BudgetTemplates.generate_dynamic_budget(
        template_id="young_professional", 
        income=45000, 
        lifestyle_factors=lifestyle_factors
    )
    
    print(f"\n=== Dynamic Budget Analysis ===")
    print(f"Template: {dynamic_budget['template_name']}")
    print(f"Income: ₱{dynamic_budget['income']:,}")
    print(f"Financial Health Score: {dynamic_budget['financial_health_score']:.1f}/100")
    print(f"Total Savings Rate: {dynamic_budget['savings_rate']:.1f}%")
    
    print(f"\n--- Budget Allocations ---")
    for category, amount in dynamic_budget['allocations_amount'].items():
        percentage = dynamic_budget['allocations_percentage'][category]
        print(f"{category.replace('_', ' ').title()}: ₱{amount:,.0f} ({percentage:.1%})")
    
    print(f"\n--- Adjustments Made ---")
    for note in dynamic_budget['adjustment_rationale']:
        print(f"• {note}")
    
    print(f"\n--- Baseline vs Adjusted Comparison ---")
    for category, changes in dynamic_budget['baseline_vs_adjusted'].items():
        if abs(changes['change']) > 0.005:  # Only show meaningful changes
            change_direction = "↗" if changes['change'] > 0 else "↘"
            print(f"{category.replace('_', ' ').title()}: {changes['baseline']:.1%} → {changes['adjusted']:.1%} {change_direction}")
