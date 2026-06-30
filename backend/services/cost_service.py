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
        nm = comp.get("name", "").lower()
        if any(k in cat for k in ["power", "energy", "solar", "battery", "esc", "charger", "supply", "voltage"]) or any(k in nm for k in ["battery", "solar", "power supply", "charger", "esc"]):
            category_group = "Power"
        elif any(k in cat for k in ["electronics", "navigation", "sensor", "controller", "board", "flight", "gps", "receiver", "mcu", "cpu", "processor", "led", "display", "screen", "wire", "module", "communication", "actuator", "indicator"]) or any(k in nm for k in ["esp32", "arduino", "pico", "sensor", "led", "wire", "gps", "display", "screen", "transceiver", "mcu", "controller"]):
            category_group = "Electronics"
        else:
            category_group = "Mechanical"
            
        subtotals[category_group] += cost_inr
        
    total_cost = sum(subtotals.values())
    
    return {
        "total_cost_inr": total_cost,
        "subtotals_inr": subtotals
    }
