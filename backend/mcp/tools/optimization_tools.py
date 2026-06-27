from typing import List, Dict, Any

def optimize_components(components: List[Dict[str, Any]]) -> Dict[str, Any]:
    optimized_list = []
    recommendations = []
    total_original_cost = sum(c.get("cost", 0) for c in components)
    saved_amount = 0.0
    
    # Run optimization rule matching based on components
    for comp in components:
        name = comp.get("name", "").lower()
        original_cost = comp.get("cost", 0)
        
        if "solar panel" in name and "flexible" in name:
            # Recommend glass panel if weight isn't critical or cheaper brand
            alternative_cost = 60.00
            diff = original_cost - alternative_cost
            saved_amount += diff
            optimized_list.append({
                "original": comp["name"],
                "optimized_alternative": "100W Rigid Monocrystalline Glass Solar Panel",
                "cost_saved": diff,
                "notes": "Reduces cost by 30% if design can accommodate rigid mounting brackets."
            })
            recommendations.append("Substitute flexible solar panel with a rigid glass panel to save $25.00 if weight budgets allow.")
            
        elif "lifepo4" in name or "battery pack" in name:
            # Recommend local source assembly
            alternative_cost = 75.00
            diff = original_cost - alternative_cost
            saved_amount += diff
            optimized_list.append({
                "original": comp["name"],
                "optimized_alternative": "DIY 4S 3.2V 10Ah LiFePO4 cells + 4S 20A BMS board",
                "cost_saved": diff,
                "notes": "Assembling cells manually reduces retail markup. Requires soldering/spot welding."
            })
            recommendations.append("Build the battery pack from individual 3.2V prismatic cells and a separate BMS module to cut power storage costs.")
            
        elif "pixhawk" in name:
            # Recommend cheaper clone or Matek board
            alternative_cost = 130.00
            diff = original_cost - alternative_cost
            saved_amount += diff
            optimized_list.append({
                "original": comp["name"],
                "optimized_alternative": "Matek H743-WING V3 Flight Controller",
                "cost_saved": diff,
                "notes": "ArduPilot-compatible, identical sensor specifications but at a significantly lower cost."
            })
            recommendations.append("Swap the Pixhawk FC with a Matek H743 controller to save $90.00 while retaining autonomous navigation features.")
            
    # Add a general recommendation if nothing matched
    if not recommendations:
        recommendations.append("Optimize mechanical fittings by consolidating 3D prints into single multi-functional brackets.")
        optimization_score = 92
    else:
        optimization_score = 88
        
    return {
        "optimized_alternatives": optimized_list,
        "recommendations": recommendations,
        "original_cost": total_original_cost,
        "optimized_cost": total_original_cost - saved_amount,
        "saved_amount": saved_amount,
        "optimization_score": optimization_score
    }
