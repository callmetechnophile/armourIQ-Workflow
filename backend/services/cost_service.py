from typing import List, Dict, Any

def calculate_total_cost(components: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates total build cost in INR (converting from USD where 1 USD = 83 INR)
    and breaks it down into categories: Electronics, Mechanical, Power.
    """
    conversion_rate = 83
    subtotals = {
        "Electronics": 0,
        "Mechanical": 0,
        "Power": 0
    }
    
    for comp in components:
        # Determine cost (defaulting to 0 if missing)
        cost_usd = float(comp.get("cost", 0.0))
        cost_inr = int(cost_usd * conversion_rate)
        
        # Classify category
        cat = comp.get("category", "").lower()
        if any(keyword in cat for keyword in ["power", "energy", "solar", "battery", "esc", "charger", "supply"]):
            category_group = "Power"
        elif any(keyword in cat for keyword in ["electronics", "navigation", "sensor", "controller", "board", "flight", "gps", "receiver"]):
            category_group = "Electronics"
        else:
            category_group = "Mechanical"
            
        subtotals[category_group] += cost_inr
        
    total_cost = sum(subtotals.values())
    
    return {
        "total_cost_inr": total_cost,
        "subtotals_inr": subtotals
    }
