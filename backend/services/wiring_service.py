from typing import List, Dict, Any

def generate_wiring_diagram(components: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generates point-to-point pin connections based on current project components.
    Categorizes connection buses (I2C, SPI, PWM, Analog, GPIO, Power).
    """
    connections = []
    
    # Identify key components present
    has_esp32 = any("esp32" in (c.get("component") or c.get("name", "")).lower() for c in components)
    has_pca9685 = any("pca9685" in (c.get("component") or c.get("name", "")).lower() for c in components)
    has_servos = any("servo" in (c.get("component") or c.get("name", "")).lower() for c in components)
    has_flex = any("flex" in (c.get("component") or c.get("name", "")).lower() for c in components)
    has_battery = any("battery" in (c.get("component") or c.get("name", "")).lower() or "lipo" in (c.get("component") or c.get("name", "")).lower() for c in components)
    
    # 1. ESP32 to PCA9685 connections (I2C Bus)
    if has_esp32 and has_pca9685:
        connections.append({
            "source": "ESP32 Board",
            "source_pin": "GPIO 21 (SDA)",
            "target": "PCA9685 Driver",
            "target_pin": "SDA",
            "color": "#eab308",  # Yellow
            "protocol": "I2C",
            "description": "I2C Serial Data line for servo steering registers"
        })
        connections.append({
            "source": "ESP32 Board",
            "source_pin": "GPIO 22 (SCL)",
            "target": "PCA9685 Driver",
            "target_pin": "SCL",
            "color": "#f8fafc",  # White/Slate
            "protocol": "I2C",
            "description": "I2C Serial Clock line to synchronize serial bus"
        })
        connections.append({
            "source": "ESP32 Board",
            "source_pin": "3.3V",
            "target": "PCA9685 Driver",
            "target_pin": "VCC",
            "color": "#ef4444",  # Red
            "protocol": "Power",
            "description": "Logic operating power rail (3.3V)"
        })
        connections.append({
            "source": "ESP32 Board",
            "source_pin": "GND",
            "target": "PCA9685 Driver",
            "target_pin": "GND",
            "color": "#09090b",  # Black
            "protocol": "Power",
            "description": "Common logic ground connection"
        })
        
    # 2. Battery to PCA9685 Servo Terminal
    if has_battery and has_pca9685:
        connections.append({
            "source": "LiPo Battery",
            "source_pin": "V+ (7.4V)",
            "target": "PCA9685 Driver",
            "target_pin": "V+ Terminal",
            "color": "#ef4444",  # Red
            "protocol": "Power",
            "description": "Primary high current rail for servo actuation"
        })
        connections.append({
            "source": "LiPo Battery",
            "source_pin": "GND (-)",
            "target": "PCA9685 Driver",
            "target_pin": "GND Terminal",
            "color": "#09090b",  # Black
            "protocol": "Power",
            "description": "Common grounding terminal to avoid signal float"
        })
        
    # 3. PCA9685 to Servos (PWM channels)
    if has_pca9685 and has_servos:
        for idx in range(5):
            connections.append({
                "source": "PCA9685 Driver",
                "source_pin": f"Channel {idx}",
                "target": "SG90 Servo Array",
                "target_pin": f"Servo {idx} PWM (Orange)",
                "color": "#f97316",  # Orange
                "protocol": "PWM",
                "description": f"Pulse-width modulation signal for finger {idx} control"
            })
        connections.append({
            "source": "PCA9685 Driver",
            "source_pin": "Channel 5",
            "target": "MG996R Servo",
            "target_pin": "PWM Signal (Orange)",
            "color": "#f97316",  # Orange
            "protocol": "PWM",
            "description": "PWM wrist control pulse line"
        })
        
    # 4. Flex Sensors to ESP32 Analog inputs (ADC channels)
    if has_esp32 and has_flex:
        pins = ["GPIO 32 (ADC0)", "GPIO 33 (ADC1)", "GPIO 34 (ADC2)", "GPIO 35 (ADC3)", "GPIO 36 (ADC4)"]
        for idx, pin in enumerate(pins):
            connections.append({
                "source": "Flex Sensor Array",
                "source_pin": f"Sensor {idx} Out",
                "target": "ESP32 Board",
                "target_pin": pin,
                "color": "#3b82f6",  # Blue
                "protocol": "Analog",
                "description": f"Analog voltage drop reporting flex bend ratio {idx}"
            })
            
    # Fallback generic wiring if none of the above are matched
    if not connections:
        connections.append({
            "source": "Core Controller",
            "source_pin": "GPIO 2",
            "target": "RGB LED indicators",
            "target_pin": "LED Input",
            "color": "#10b981",  # Green
            "protocol": "GPIO",
            "description": "Status blink output pin"
        })
        
    return {
        "connections": connections
    }
