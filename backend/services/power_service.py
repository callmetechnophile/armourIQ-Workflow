from typing import List, Dict, Any

# Component database of operating specifications
POWER_DATABASE = {
    "esp32": {"voltage": 3.3, "current": 80, "peak_current": 240, "standby": 0.015},
    "pca9685": {"voltage": 5.0, "current": 10, "peak_current": 15, "standby": 0.1},
    "sg90": {"voltage": 5.0, "current": 500, "peak_current": 2500, "standby": 25.0}, # Set of 5
    "mg996r": {"voltage": 6.0, "current": 250, "peak_current": 2500, "standby": 10.0},
    "flex sensor": {"voltage": 3.3, "current": 5, "peak_current": 10, "standby": 0.0},
    "brushless motor": {"voltage": 22.2, "current": 32000, "peak_current": 120000, "standby": 0.0}, # Set of 4 (quad)
    "esc": {"voltage": 22.2, "current": 600, "peak_current": 1000, "standby": 40.0}, # Set of 4
    "pixhawk": {"voltage": 5.3, "current": 500, "peak_current": 800, "standby": 150.0},
    "gps": {"voltage": 5.0, "current": 80, "peak_current": 120, "standby": 5.0},
    "telemetry": {"voltage": 5.0, "current": 100, "peak_current": 500, "standby": 10.0},
    "suction motor": {"voltage": 24.0, "current": 8000, "peak_current": 15000, "standby": 0.0},
    "solar panel": {"voltage": 18.0, "current": 0, "peak_current": 0, "standby": 0.0}, # Power generator
    "charge controller": {"voltage": 12.0, "current": 20, "peak_current": 50, "standby": 10.0},
    "battery": {"voltage": 12.8, "current": 0, "peak_current": 0, "standby": 0.0} # Storage
}

def get_component_power_specs(name: str) -> Dict[str, float]:
    name_lower = name.lower()
    for key, specs in POWER_DATABASE.items():
        if key in name_lower:
            return specs
    # Fallback default low power sensor
    return {"voltage": 5.0, "current": 20, "peak_current": 50, "standby": 1.0}

def calculate_power_budget(components: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates total power load, peak load, standby load, and groups by voltage domains.
    """
    power_items = []
    total_nominal_mA = 0.0
    total_peak_mA = 0.0
    total_standby_mA = 0.0
    
    voltage_domains = set()
    battery_capacity_Ah = 0.0
    battery_voltage = 0.0
    
    for comp in components:
        # Resolve either "component" or "name" key
        name = comp.get("component") or comp.get("name", "")
        specs = get_component_power_specs(name)
        
        # Check if battery source is present to extract capacity
        if "battery" in name.lower() or "lipo" in name.lower():
            if "2200" in name:
                battery_capacity_Ah = 2.2
                battery_voltage = 7.4
            elif "10ah" in name or "10000" in name:
                battery_capacity_Ah = 10.0
                battery_voltage = 12.8 if "lifepo4" in name.lower() else 22.2
            else:
                battery_capacity_Ah = 2.0
                battery_voltage = 5.0
                
        # Do not add power sources (batteries, solar panels) to active power load sums
        if "battery" in name.lower() or "solar panel" in name.lower():
            voltage_domains.add(specs["voltage"])
            power_items.append({
                "component": name,
                "voltage": specs["voltage"],
                "nominal_current": 0.0,
                "peak_current": 0.0,
                "standby_current": 0.0,
                "is_source": True
            })
            continue
            
        voltage_domains.add(specs["voltage"])
        
        nominal = float(specs["current"])
        peak = float(specs["peak_current"])
        standby = float(specs["standby"])
        
        total_nominal_mA += nominal
        total_peak_mA += peak
        total_standby_mA += standby
        
        power_items.append({
            "component": name,
            "voltage": specs["voltage"],
            "nominal_current": nominal,
            "peak_current": peak,
            "standby_current": standby,
            "is_source": False
        })
        
    # Convert load back to Watts based on system voltage (using average or battery voltage)
    sys_voltage = battery_voltage if battery_voltage > 0 else 5.0
    total_load_watts = round((total_nominal_mA / 1000.0) * sys_voltage, 2)
    peak_load_watts = round((total_peak_mA / 1000.0) * sys_voltage, 2)
    
    # Calculate runtime
    runtime_hours = estimate_runtime(battery_capacity_Ah, total_nominal_mA)
    
    # Warnings checks
    warnings = validate_power_constraints(power_items, battery_capacity_Ah, total_peak_mA, sys_voltage)
    
    return {
        "power_items": power_items,
        "summary": {
            "total_power_load_w": total_load_watts,
            "peak_current_a": round(total_peak_mA / 1000.0, 2),
            "peak_power_load_w": peak_load_watts,
            "standby_load_ma": total_standby_mA,
            "battery_voltage_v": sys_voltage,
            "battery_capacity_ah": battery_capacity_Ah,
            "estimated_runtime_hours": runtime_hours,
            "voltage_domains_count": len(voltage_domains)
        },
        "warnings": warnings
    }

def estimate_runtime(capacity_ah: float, current_draw_ma: float) -> float:
    """
    Formula: Runtime = Battery Capacity / Total Current Draw
    """
    if capacity_ah <= 0 or current_draw_ma <= 0:
        return 0.0
    current_a = current_draw_ma / 1000.0
    return round(capacity_ah / current_a, 2)

def validate_power_constraints(power_items: List[Dict[str, Any]], capacity_ah: float, peak_current_ma: float, system_voltage: float) -> List[str]:
    warnings = []
    
    # Check 1: Overcurrent risk (e.g. LiPo standard discharge rating vs peak current load)
    # 2200mAh 25C LiPo can output 2.2 * 25 = 55A. Peak load of robotic hand is ~5.2A (well within limit).
    # If peak current is extremely high and battery is low or not configured
    if capacity_ah > 0:
        max_safe_current_a = capacity_ah * 25.0  # Assumes 25C discharge safe threshold
        peak_a = peak_current_ma / 1000.0
        if peak_a > max_safe_current_a:
            warnings.append(f"Overcurrent Risk: Peak load ({peak_a}A) exceeds battery safe continuous output limit ({max_safe_current_a}A).")
            
    # Check 2: Battery insufficient (runtime too short, less than 0.5 hours / 30 mins)
    if capacity_ah > 0:
        current_draw = sum(i["nominal_current"] for i in power_items if not i["is_source"])
        if current_draw > 0:
            runtime = estimate_runtime(capacity_ah, current_draw)
            if runtime < 0.5:
                warnings.append(f"Battery Insufficient: Estimated system runtime is too short ({runtime} hrs). Consider upgrading battery capacity.")
    elif capacity_ah == 0:
        warnings.append("Power Source Warning: No active battery power source detected in the extraction pipeline.")
        
    # Check 3: Voltage domain logic mismatches
    # E.g. ESP32 (3.3V) communicating with SG90 (5.0V) directly without logic-level shifters.
    has_3v3 = any(i["voltage"] == 3.3 for i in power_items)
    has_5v = any(i["voltage"] == 5.0 for i in power_items)
    if has_3v3 and has_5v:
        warnings.append("Voltage Mismatch Warning: Bidirectional logic lines between 3.3V controller (ESP32) and 5.0V nodes (PCA9685/Servos) require logic shifters.")
        
    return warnings
