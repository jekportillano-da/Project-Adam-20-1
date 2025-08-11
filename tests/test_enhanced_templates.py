"""
Comprehensive test of the Enhanced Budget Templates system
Demonstrates dynamic adjustments based on various lifestyle factors
"""

from budget_templates import BudgetTemplates

def test_enhanced_budget_templates():
    """Test various scenarios with different lifestyle factors"""
    
    print("🧪 Enhanced Budget Templates - Comprehensive Test")
    print("=" * 60)
    
    # Test Case 1: Young professional with high rent
    print("\n📋 Test Case 1: Young Professional with High Rent")
    print("-" * 50)
    
    lifestyle_factors_1 = {
        "rent_pct": 0.42,  # 42% of income on rent (very high)
        "age": 26,
        "location": "metro",
        "target_savings_rate": 0.15
    }
    
    budget_1 = BudgetTemplates.generate_dynamic_budget(
        template_id="young_professional",
        income=35000,
        lifestyle_factors=lifestyle_factors_1
    )
    
    print(f"Income: ₱{budget_1['income']:,}")
    print(f"Financial Health Score: {budget_1['financial_health_score']:.1f}/100")
    print(f"Savings Rate: {budget_1['savings_rate']:.1f}%")
    print("\nKey Allocations:")
    print(f"  Housing: ₱{budget_1['allocations_amount']['housing']:,.0f} ({budget_1['allocations_percentage']['housing']:.1%})")
    print(f"  Emergency Fund: ₱{budget_1['allocations_amount']['emergency_fund']:,.0f} ({budget_1['allocations_percentage']['emergency_fund']:.1%})")
    print(f"  Investments: ₱{budget_1['allocations_amount']['investments']:,.0f} ({budget_1['allocations_percentage']['investments']:.1%})")
    print("\nAdjustments Made:")
    for note in budget_1['adjustment_rationale']:
        print(f"  • {note}")
    
    # Test Case 2: Family breadwinner with kids and debt
    print("\n📋 Test Case 2: Family Breadwinner with Kids and Debt")
    print("-" * 50)
    
    lifestyle_factors_2 = {
        "has_kids": True,
        "dependents": 2,
        "debt_ratio": 0.22,  # 22% debt payments
        "car_payment": 12000,
        "age": 38,
        "location": "urban",
        "income_stability": "stable"
    }
    
    budget_2 = BudgetTemplates.generate_dynamic_budget(
        template_id="family_breadwinner",
        income=55000,
        lifestyle_factors=lifestyle_factors_2
    )
    
    print(f"Income: ₱{budget_2['income']:,}")
    print(f"Financial Health Score: {budget_2['financial_health_score']:.1f}/100")
    print(f"Savings Rate: {budget_2['savings_rate']:.1f}%")
    print("\nKey Allocations:")
    print(f"  Food: ₱{budget_2['allocations_amount']['food']:,.0f} ({budget_2['allocations_percentage']['food']:.1%})")
    print(f"  Transportation: ₱{budget_2['allocations_amount']['transportation']:,.0f} ({budget_2['allocations_percentage']['transportation']:.1%})")
    print(f"  Emergency Fund: ₱{budget_2['allocations_amount']['emergency_fund']:,.0f} ({budget_2['allocations_percentage']['emergency_fund']:.1%})")
    print("\nAdjustments Made:")
    for note in budget_2['adjustment_rationale']:
        print(f"  • {note}")
    
    # Test Case 3: Entrepreneur with variable income
    print("\n📋 Test Case 3: Entrepreneur with Variable Income")
    print("-" * 50)
    
    lifestyle_factors_3 = {
        "income_stability": "variable",
        "age": 33,
        "target_savings_rate": 0.25,  # High savings target due to income volatility
        "location": "urban",
        "is_entrepreneur": True,
        "rent_pct": 0.28  # Lower housing costs
    }
    
    budget_3 = BudgetTemplates.generate_dynamic_budget(
        template_id="entrepreneur",
        income=75000,
        lifestyle_factors=lifestyle_factors_3
    )
    
    print(f"Income: ₱{budget_3['income']:,}")
    print(f"Financial Health Score: {budget_3['financial_health_score']:.1f}/100")
    print(f"Savings Rate: {budget_3['savings_rate']:.1f}%")
    print("\nKey Allocations:")
    print(f"  Housing: ₱{budget_3['allocations_amount']['housing']:,.0f} ({budget_3['allocations_percentage']['housing']:.1%})")
    print(f"  Emergency Fund: ₱{budget_3['allocations_amount']['emergency_fund']:,.0f} ({budget_3['allocations_percentage']['emergency_fund']:.1%})")
    print(f"  Investments: ₱{budget_3['allocations_amount']['investments']:,.0f} ({budget_3['allocations_percentage']['investments']:.1%})")
    print("\nAdjustments Made:")
    for note in budget_3['adjustment_rationale']:
        print(f"  • {note}")
    
    # Test Case 4: OFW with aggressive savings goals
    print("\n📋 Test Case 4: OFW with Aggressive Savings Goals")
    print("-" * 50)
    
    lifestyle_factors_4 = {
        "is_ofw": True,
        "location": "overseas",
        "age": 29,
        "target_savings_rate": 0.35,  # Very aggressive savings
        "rent_pct": 0.22,  # Company housing
        "income_stability": "stable"
    }
    
    budget_4 = BudgetTemplates.generate_dynamic_budget(
        template_id="ofw_remittance",
        income=85000,
        lifestyle_factors=lifestyle_factors_4
    )
    
    print(f"Income: ₱{budget_4['income']:,}")
    print(f"Financial Health Score: {budget_4['financial_health_score']:.1f}/100")
    print(f"Savings Rate: {budget_4['savings_rate']:.1f}%")
    print("\nKey Allocations:")
    print(f"  Housing: ₱{budget_4['allocations_amount']['housing']:,.0f} ({budget_4['allocations_percentage']['housing']:.1%})")
    print(f"  Emergency Fund: ₱{budget_4['allocations_amount']['emergency_fund']:,.0f} ({budget_4['allocations_percentage']['emergency_fund']:.1%})")
    print(f"  Investments: ₱{budget_4['allocations_amount']['investments']:,.0f} ({budget_4['allocations_percentage']['investments']:.1%})")
    print("\nAdjustments Made:")
    for note in budget_4['adjustment_rationale']:
        print(f"  • {note}")
    
    # Test Case 5: Senior Executive with optimization focus
    print("\n📋 Test Case 5: Senior Executive Optimization")
    print("-" * 50)
    
    lifestyle_factors_5 = {
        "age": 52,
        "job_level": "executive",
        "rent_pct": 0.24,  # Good housing deal
        "target_savings_rate": 0.30,
        "location": "metro"
    }
    
    budget_5 = BudgetTemplates.generate_dynamic_budget(
        template_id="senior_executive",
        income=95000,
        lifestyle_factors=lifestyle_factors_5
    )
    
    print(f"Income: ₱{budget_5['income']:,}")
    print(f"Financial Health Score: {budget_5['financial_health_score']:.1f}/100")
    print(f"Savings Rate: {budget_5['savings_rate']:.1f}%")
    print("\nKey Allocations:")
    print(f"  Housing: ₱{budget_5['allocations_amount']['housing']:,.0f} ({budget_5['allocations_percentage']['housing']:.1%})")
    print(f"  Emergency Fund: ₱{budget_5['allocations_amount']['emergency_fund']:,.0f} ({budget_5['allocations_percentage']['emergency_fund']:.1%})")
    print(f"  Investments: ₱{budget_5['allocations_amount']['investments']:,.0f} ({budget_5['allocations_percentage']['investments']:.1%})")
    print("\nAdjustments Made:")
    for note in budget_5['adjustment_rationale']:
        print(f"  • {note}")
    
    # Summary comparison
    print("\n📊 Summary Comparison")
    print("=" * 60)
    
    test_cases = [
        ("Young Professional (High Rent)", budget_1),
        ("Family Breadwinner", budget_2),
        ("Entrepreneur (Variable Income)", budget_3),
        ("OFW (Aggressive Savings)", budget_4),
        ("Senior Executive", budget_5)
    ]
    
    print(f"{'Scenario':<25} {'Income':<12} {'Health':<8} {'Savings%':<10} {'Housing%':<10} {'Emergency%':<10}")
    print("-" * 85)
    
    for name, budget in test_cases:
        print(f"{name:<25} ₱{budget['income']:>8,} {budget['financial_health_score']:>6.1f} {budget['savings_rate']:>8.1f}% {budget['allocations_percentage']['housing']*100:>8.1f}% {budget['allocations_percentage']['emergency_fund']*100:>9.1f}%")
    
    print("\n✅ All test cases completed successfully!")
    print("🎯 The enhanced budget templates demonstrate:")
    print("   • Dynamic adjustments based on real-world factors")
    print("   • Intelligent trade-offs between categories")
    print("   • Maintainance of financial health across scenarios")
    print("   • Clear rationale for every adjustment made")

if __name__ == "__main__":
    test_enhanced_budget_templates()
