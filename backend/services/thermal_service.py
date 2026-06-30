import math
from typing import List, Dict, Any

def estimate_heat_generation(component: Dict[str, Any]) -> float:
    """
    Estimate heat generation in Watts based on nominal/peak current and voltage.
    """
    voltage = float(component.get("voltage", 5.0))
    current_ma = float(component.get("nominal_current", component.get("current_ma", 100.0)))
    # Power = V * I (in Amps)
    power_w = voltage * (current_ma / 1000.0)
    
    # Actuators and regulators have higher thermal losses (efficiency factor)
    name = (component.get("component") or component.get("name", "")).lower()
    if "motor" in name or "servo" in name:
        efficiency = 0.65  # 35% converted to heat
        heat_w = power_w * (1.0 - efficiency)
    elif "regulator" in name or "buck" in name or "converter" in name:
        efficiency = 0.85  # 15% converted to heat
        heat_w = power_w * (1.0 - efficiency)
    elif "mosfet" in name or "transistor" in name:
        # MOSFET static thermal dissipation: I^2 * R_ds_on
        r_ds_on = 0.05 # typical 50 mOhm
        current_a = current_ma / 1000.0
        heat_w = (current_a ** 2) * r_ds_on
    else:
        heat_w = power_w * 0.95 # IC logic is mostly dissipation
        
    return round(heat_w, 3)

def recommend_cooling(component_name: str, risk_level: str) -> str:
    """
    Recommend appropriate cooling mitigation based on thermal risk level and component type.
    """
    name = component_name.lower()
    if risk_level == "Critical":
        if "motor" in name or "servo" in name:
            return "IMMEDIATE: Add active fan cooling, aluminum heat sinks, and decrease servo duty cycle."
        if "regulator" in name or "buck" in name:
            return "IMMEDIATE: Add high-profile heat sink, external fan ventilation, and upgrade regulator power rating."
        return "IMMEDIATE: Halt execution. Add active fan ventilation and check for logic level short circuits."
        
    if risk_level == "High":
        if "motor" in name or "servo" in name:
            return "Recommend passive copper heat sinks and 10% sleep intervals in loop firmware."
        if "regulator" in name or "buck" in name:
            return "Affix a passive stick-on aluminum heatsink (TO-220 size)."
        return "Ensure adequate ventilation slots in the physical prototype enclosure."
        
    if risk_level == "Medium":
        return "Ensure component is not placed flush against heat-sensitive materials (like 3D printed PLA)."
        
    return "No active cooling required. Normal convection air flow is sufficient."

def analyze_thermal_risk(components: List[Dict[str, Any]], enclosure_temp: float = 25.0) -> List[Dict[str, Any]]:
    """
    Estimate overheating risk for each component using physics-based heat calculations.
    """
    thermal_reports = []
    
    for c in components:
        comp_name = c.get("component") or c.get("name", "Unknown")
        name_lower = comp_name.lower()
        
        # Determine datasheet limit defaults
        max_temp_ds = 85.0 # default IC max temperature in C
        r_theta_ja = 62.5 # default thermal resistance C/W (typical for DIP/SOIC packages)
        
        if "motor" in name_lower or "servo" in name_lower:
            max_temp_ds = 65.0
            r_theta_ja = 45.0
        elif "battery" in name_lower or "lipo" in name_lower:
            max_temp_ds = 60.0
            r_theta_ja = 15.0 # batteries have large thermal mass, low Rth
        elif "regulator" in name_lower or "buck" in name_lower:
            max_temp_ds = 125.0
            r_theta_ja = 50.0
        elif "mosfet" in name_lower or "transistor" in name_lower:
            max_temp_ds = 150.0
            r_theta_ja = 80.0
            
        heat_w = estimate_heat_generation(c)
        
        # Physics calculation: T_estimated = T_ambient + (Heat * R_theta)
        estimated_temp = enclosure_temp + (heat_w * r_theta_ja)
        
        # Risk level determination based on margin to datasheet limit
        margin = max_temp_ds - estimated_temp
        
        if margin <= 0 or estimated_temp > 100:
            risk_level = "Critical"
            warning = f"Component exceeds datasheet limit ({max_temp_ds}°C). High probability of permanent thermal damage!"
        elif margin < 15:
            risk_level = "High"
            warning = f"Component is operating close to its thermal threshold ({max_temp_ds}°C). Active cooling required."
        elif margin < 35:
            risk_level = "Medium"
            warning = f"Elevated temperature detected. Monitor enclosure ventilation."
        else:
            risk_level = "Low"
            warning = f"Operating well within safe limits (Margin: {round(margin, 1)}°C)."
            
        thermal_reports.append({
            "component": comp_name,
            "estimated_temp": round(estimated_temp, 1),
            "max_temp": max_temp_ds,
            "heat_w": heat_w,
            "risk_level": risk_level,
            "warning": warning,
            "cooling_recommendation": recommend_cooling(comp_name, risk_level)
        })
        
    return thermal_reports
