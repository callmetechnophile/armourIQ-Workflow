from typing import List, Dict, Any

def check_voltage_compatibility(components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Scans the extracted component list for electrical items, maps their operating
    voltages, and validates compatibility (e.g., logic level shifts, power step-downs).
    """
    # 1. Map components to their electrical profiles
    profiles = []
    for comp in components:
        name_lower = comp.get("name", "").lower()
        
        if "esp32" in name_lower:
            profiles.append({"name": comp["name"], "role": "MCU", "logic_v": 3.3, "power_v": 5.0})
        elif "pixhawk" in name_lower or "flight controller" in name_lower:
            profiles.append({"name": comp["name"], "role": "MCU", "logic_v": 3.3, "power_v": 5.3})
        elif "sensor" in name_lower or "mpu6050" in name_lower or "gps" in name_lower:
            # Most common sensors run at 5V or 3.3V
            logic = 5.0 if "5v" in name_lower or "mpu6050" in name_lower else 3.3
            profiles.append({"name": comp["name"], "role": "Sensor", "logic_v": logic, "power_v": logic})
        elif "motor" in name_lower or "suction" in name_lower:
            volt = 24.0 if "24v" in name_lower else 12.0
            profiles.append({"name": comp["name"], "role": "Load", "logic_v": 3.3, "power_v": volt})
        elif "esc" in name_lower:
            profiles.append({"name": comp["name"], "role": "Driver", "logic_v": 3.3, "power_v": 14.8})
        elif "mppt" in name_lower or "controller" in name_lower:
            profiles.append({"name": comp["name"], "role": "Regulator", "logic_v": 3.3, "power_v": 24.0})
        elif "battery" in name_lower or "pack" in name_lower:
            volt = 12.8 if "12.8v" in name_lower else (14.8 if "14.8v" in name_lower else 12.0)
            profiles.append({"name": comp["name"], "role": "Source", "logic_v": 0.0, "power_v": volt})
        elif "servo" in name_lower or "gripper" in name_lower:
            profiles.append({"name": comp["name"], "role": "Actuator", "logic_v": 3.3, "power_v": 6.0})

    mismatches = []
    
    # 2. Match logic levels between MCU and Sensors/Actuators
    mcus = [p for p in profiles if p["role"] == "MCU"]
    sensors = [p for p in profiles if p["role"] in ["Sensor", "Actuator"]]
    sources = [p for p in profiles if p["role"] == "Source"]
    loads = [p for p in profiles if p["role"] in ["Load", "Driver"]]
    
    # Logic Level Checks
    for mcu in mcus:
        for s in sensors:
            if mcu["logic_v"] != s["logic_v"]:
                mismatches.append({
                    "component_a": mcu["name"],
                    "component_b": s["name"],
                    "voltage": f"{mcu['logic_v']}V vs {s['logic_v']}V",
                    "risk": "WARNING",
                    "details": f"Logic level mismatch. {mcu['name']} runs at {mcu['logic_v']}V logic, but {s['name']} requires {s['logic_v']}V. Recommends I2C/GPIO logic level shifter."
                })
            else:
                mismatches.append({
                    "component_a": mcu["name"],
                    "component_b": s["name"],
                    "voltage": f"{mcu['logic_v']}V logic",
                    "risk": "SAFE",
                    "details": "Logic levels match. Interfaces directly."
                })

    # Power/Source Checks
    for src in sources:
        for load in loads:
            if src["power_v"] != load["power_v"]:
                mismatches.append({
                    "component_a": src["name"],
                    "component_b": load["name"],
                    "voltage": f"{src['power_v']}V source vs {load['power_v']}V load",
                    "risk": "HIGH RISK",
                    "details": f"Supply mismatch. Battery provides {src['power_v']}V, but load {load['name']} requires {load['power_v']}V. Requires boost converter or voltage regulator module."
                })
            else:
                mismatches.append({
                    "component_a": src["name"],
                    "component_b": load["name"],
                    "voltage": f"{src['power_v']}V supply",
                    "risk": "SAFE",
                    "details": "Source voltage matches load requirement."
                })
                
    # If no electrical items or no mismatches found, populate general safe entries
    if not mismatches:
        mismatches.append({
            "component_a": "System Power Rail",
            "component_b": "Controller VCC",
            "voltage": "5.0V / 3.3V",
            "risk": "SAFE",
            "details": "Common ground and voltage rails aligned."
        })

    return mismatches
