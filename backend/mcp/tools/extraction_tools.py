import os
import json
from typing import List, Dict, Any

def extract_components(raw_text: str) -> List[Dict[str, Any]]:
    # Check if GROQ_API_KEY is present to perform dynamic LLM-based component extraction
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if groq_api_key and not groq_api_key.startswith("gsk_placeholder"):
        try:
            import httpx
            prompt = (
                "You are an expert hardware prototyping and design engineer.\n"
                f"Analyze the user's design target: '{raw_text}'\n"
                "Extract or generate a list of 4 to 6 required electronics and mechanical components to build this prototype.\n"
                "For each component, estimate its market price in USD (keep it realistic, e.g., $5 to $200 depending on the component).\n\n"
                "Output ONLY a valid JSON list. Do not include markdown wraps (like ```json) or any text outside of the JSON block.\n"
                "Each component item in the list MUST have exactly these fields:\n"
                "- category: string (e.g., 'Core Controller', 'Power Supply', 'Sensors', 'Actuators', 'Structural')\n"
                "- name: string (the specific hardware part name, e.g., 'ESP32 Development Board')\n"
                "- cost: float (the estimated cost in USD, e.g., 7.50)\n"
                "- notes: string (a short explanation of its purpose in the prototype)\n"
                "Example format: [{\"category\": \"Sensors\", \"name\": \"HC-SR04 Ultrasonic Sensor\", \"cost\": 3.50, \"notes\": \"Measures distance to target objects.\"}]"
            )
            
            payload = {
                "model": "gemma2-9b-it",
                "messages": [
                    {"role": "system", "content": "You are a precise JSON generator. Output only JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "response_format": {"type": "json_object"}
            }
            
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            
            with httpx.Client(timeout=10.0) as client:
                res = client.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
                if res.status_code == 200:
                    content = res.json()["choices"][0]["message"]["content"].strip()
                    parsed = json.loads(content)
                    if isinstance(parsed, list):
                        return parsed
                    elif isinstance(parsed, dict) and "components" in parsed:
                        return parsed["components"]
        except Exception as e:
            print(f"[Extraction] Dynamic LLM extraction failed: {e}. Falling back to static mapping.")

    # Static fallback maps
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
    elif "hand" in text_lower or "bionic" in text_lower or "robotic" in text_lower:
        return [
            {
                "category": "Core Controller",
                "name": "ESP32-WROOM-32D Development Board",
                "cost": 7.50,
                "notes": "Dual-core processor with Wi-Fi/Bluetooth for hand gestures and wireless glove inputs."
            },
            {
                "category": "Servo Driver",
                "name": "PCA9685 16-Ch PWM Servo Driver Board",
                "cost": 5.50,
                "notes": "I2C interface to control up to 16 servos independently, reducing GPIO pin usage."
            },
            {
                "category": "Actuators",
                "name": "SG90 9g Micro Servo Motors (5x Set)",
                "cost": 15.00,
                "notes": "Actuates individual fingers using tensioned wire cables."
            },
            {
                "category": "Actuators",
                "name": "MG996R High-Torque Metal Gear Servo Motor",
                "cost": 9.50,
                "notes": "Wrist flexion and extension actuation with high holding torque."
            },
            {
                "category": "Power Source",
                "name": "7.4V 2S 2200mAh 25C LiPo Battery Pack",
                "cost": 18.00,
                "notes": "High discharge capability to supply transient current demands of multiple active servos."
            },
            {
                "category": "Mechanical Frame",
                "name": "PLA Filament for 3D Printed Robotic Hand Structure",
                "cost": 16.00,
                "notes": "Chassis structures, fingers links, wrist mount components."
            },
            {
                "category": "Sensors",
                "name": "2.2 Inch Resistor Flex Sensors (5x Set)",
                "cost": 25.00,
                "notes": "Glove sensor array to measure finger bends and send analog control signals."
            }
        ]
    else:
        # Generic engineering BOM fallback
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
