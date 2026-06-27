from typing import List, Dict, Any

def extract_components(raw_text: str) -> List[Dict[str, Any]]:
    text_lower = raw_text.lower()
    if "solar" in text_lower or "vacuum" in text_lower:
        return [
            {
                "category": "Propulsion / Suction",
                "name": "Brushless DC Suction Motor (24V, 100K RPM)",
                "cost": 45.00,
                "notes": "Generates 15 kPa vacuum suction pressure. Requires ESC."
            },
            {
                "category": "Power Supply",
                "name": "100W Flexible Monocrystalline Solar Panel",
                "cost": 85.00,
                "notes": "Lightweight, can be mounted directly on the vacuum body."
            },
            {
                "category": "Electronics / Power Control",
                "name": "12V/24V 20A MPPT Solar Charge Controller",
                "cost": 30.00,
                "notes": "Enables efficient power harvesting under partial cloud cover."
            },
            {
                "category": "Energy Storage",
                "name": "12.8V 10Ah LiFePO4 Lithium Iron Phosphate Battery Pack",
                "cost": 90.00,
                "notes": "Deep cycle safety buffer. Long lifespan compared to LiPo."
            },
            {
                "category": "Structural / Mechanical",
                "name": "Modular Cyclonic Dust Filter Assembly",
                "cost": 25.00,
                "notes": "Removes large dust particles before they hit the impeller."
            },
            {
                "category": "Housing & Attachments",
                "name": "ABS Filament for 3D Printed Housing and Hose Adapters",
                "cost": 20.00,
                "notes": "Used for customized ergonomic chassis printing."
            }
        ]
    elif "drone" in text_lower or "delivery" in text_lower:
        return [
            {
                "category": "Electronics / Navigation",
                "name": "Pixhawk 6C Flight Controller with M8N GPS Module",
                "cost": 220.00,
                "notes": "Core autopilot system supporting autonomous waypoints."
            },
            {
                "category": "Propulsion",
                "name": "620KV Brushless Motors (4x Set)",
                "cost": 160.00,
                "notes": "Provides high torque and payload lifting capability."
            },
            {
                "category": "Electronics / Control",
                "name": "40A DShot600 ESCs (4x Set)",
                "cost": 80.00,
                "notes": "Drives the brushless motors with telemetric RPM feedback."
            },
            {
                "category": "Energy Storage",
                "name": "22.2V 6S 10000mAh 25C LiPo Battery Pack",
                "cost": 150.00,
                "notes": "High discharge rating to sustain lift for heavy payloads."
            },
            {
                "category": "Structure",
                "name": "650mm Carbon Fiber Quadcopter Frame",
                "cost": 120.00,
                "notes": "High rigidity and ultra lightweight design."
            },
            {
                "category": "Actuators / Payload",
                "name": "PWM Controlled Servo Cargo Release Hook",
                "cost": 35.00,
                "notes": "Triggered via transmitter or autopilot at target coordinates."
            },
            {
                "category": "Communication",
                "name": "915MHz 100mW Telemetry Link Transceiver Set",
                "cost": 50.00,
                "notes": "Allows real-time ground control station monitoring up to 5km."
            }
        ]
    else:
        # Generic engineering BOM
        return [
            {
                "category": "Core Controller",
                "name": "ESP32-WROOM-32D Development Board",
                "cost": 7.50,
                "notes": "Provides Wi-Fi and Bluetooth connectivity for general control."
            },
            {
                "category": "Power Supply",
                "name": "5V 3A DC Wall Power Adapter",
                "cost": 12.00,
                "notes": "Standard power source."
            },
            {
                "category": "Mechanical Frame",
                "name": "Laser-cut Acrylic Base Sheet",
                "cost": 15.00,
                "notes": "Sturdy base for prototype mounting."
            },
            {
                "category": "Indicators",
                "name": "RGB LED status indicators and wires pack",
                "cost": 5.00,
                "notes": "Basic visual feedback breadboard wires."
            }
        ]
