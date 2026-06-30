from typing import List, Dict, Any

def generate_pin_map(components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generates a pin configuration connection map between MCUs (ESP32/Pixhawk) 
    and periferal components (Sensors, Motors, GPS, Drivers) categorized by protocol.
    """
    pin_map = []
    
    # Identify the controller card
    mcu_name = "Controller Board"
    is_esp32 = False
    is_pixhawk = False
    
    for comp in components:
        name_lower = comp.get("name", "").lower()
        if "esp32" in name_lower:
            mcu_name = "ESP32 DevKit"
            is_esp32 = True
            break
        elif "pixhawk" in name_lower or "flight controller" in name_lower:
            mcu_name = "Pixhawk 6C"
            is_pixhawk = True
            break

    # Default to ESP32 mapping if no specific controller is present
    if not is_esp32 and not is_pixhawk:
        mcu_name = "ESP32 Core Module"
        is_esp32 = True

    # Scan peripheral components and map connections
    for comp in components:
        name = comp.get("name", "")
        name_lower = name.lower()
        
        # Avoid connecting MCU to itself
        if "esp32" in name_lower or "pixhawk" in name_lower or "flight controller" in name_lower:
            continue
            
        # 1. I2C Sensors (Compass, MPU6050, IMU)
        if any(keyword in name_lower for keyword in ["compass", "mpu6050", "imu", "gyro", "accelerometer", "display", "oled"]):
            if is_esp32:
                pin_map.append({"component": mcu_name, "pin": "GPIO21", "connected_to": f"{name} (SDA)", "type": "I2C"})
                pin_map.append({"component": mcu_name, "pin": "GPIO22", "connected_to": f"{name} (SCL)", "type": "I2C"})
            elif is_pixhawk:
                pin_map.append({"component": mcu_name, "pin": "I2C1 SDA (Pin 3)", "connected_to": f"{name} (SDA)", "type": "I2C"})
                pin_map.append({"component": mcu_name, "pin": "I2C1 SCL (Pin 4)", "connected_to": f"{name} (SCL)", "type": "I2C"})
                
        # 2. UART Peripherals (GPS, Telemetry)
        elif any(keyword in name_lower for keyword in ["gps", "telemetry", "radio", "receiver", "lidar"]):
            if is_esp32:
                pin_map.append({"component": mcu_name, "pin": "GPIO16 (RX2)", "connected_to": f"{name} (TX)", "type": "UART"})
                pin_map.append({"component": mcu_name, "pin": "GPIO17 (TX2)", "connected_to": f"{name} (RX)", "type": "UART"})
            elif is_pixhawk:
                pin_map.append({"component": mcu_name, "pin": "TELEM1 RX (Pin 2)", "connected_to": f"{name} (TX)", "type": "UART"})
                pin_map.append({"component": mcu_name, "pin": "TELEM1 TX (Pin 3)", "connected_to": f"{name} (RX)", "type": "UART"})
                
        # 3. PWM Actuators & Motors (ESC, Suction, Servos, Gripper)
        elif any(keyword in name_lower for keyword in ["esc", "motor", "suction", "servo", "gripper", "actuator"]):
            if is_esp32:
                pin_map.append({"component": mcu_name, "pin": "GPIO25 (PWM1)", "connected_to": f"{name} (PWM)", "type": "PWM"})
                pin_map.append({"component": mcu_name, "pin": "GPIO26 (PWM2)", "connected_to": f"{name} (Signal)", "type": "PWM"})
            elif is_pixhawk:
                pin_map.append({"component": mcu_name, "pin": "FMU OUT 1 (PWM)", "connected_to": f"{name} Channel 1 (PWM)", "type": "PWM"})
                pin_map.append({"component": mcu_name, "pin": "FMU OUT 2 (PWM)", "connected_to": f"{name} Channel 2 (PWM)", "type": "PWM"})

        # 4. SPI Devices (SD Card, Flash memory, Displays)
        elif any(keyword in name_lower for keyword in ["sd card", "flash", "logging", "spi"]):
            if is_esp32:
                pin_map.append({"component": mcu_name, "pin": "GPIO23 (MOSI)", "connected_to": f"{name} (MOSI)", "type": "SPI"})
                pin_map.append({"component": mcu_name, "pin": "GPIO19 (MISO)", "connected_to": f"{name} (MISO)", "type": "SPI"})
                pin_map.append({"component": mcu_name, "pin": "GPIO18 (SCK)", "connected_to": f"{name} (SCK)", "type": "SPI"})
                pin_map.append({"component": mcu_name, "pin": "GPIO5 (CS)", "connected_to": f"{name} (CS)", "type": "SPI"})
            elif is_pixhawk:
                pin_map.append({"component": mcu_name, "pin": "SPI MOSI", "connected_to": f"{name} (MOSI)", "type": "SPI"})
                pin_map.append({"component": mcu_name, "pin": "SPI MISO", "connected_to": f"{name} (MISO)", "type": "SPI"})

        # 5. Analog / Digital inputs (Current sensors, battery monitors, limits switches)
        elif any(keyword in name_lower for keyword in ["current", "battery voltage", "divider", "limit"]):
            ptype = "Analog" if "current" in name_lower or "voltage" in name_lower else "Digital"
            if is_esp32:
                pin_map.append({"component": mcu_name, "pin": "GPIO34 (ADC1)", "connected_to": f"{name} (OUT)", "type": ptype})
            elif is_pixhawk:
                pin_map.append({"component": mcu_name, "pin": "ADC IN", "connected_to": f"{name} (OUT)", "type": ptype})

    # If no connections could be mapped, provide standard defaults
    if not pin_map:
        pin_map.extend([
            {"component": mcu_name, "pin": "GPIO21 (SDA)", "connected_to": "Default Sensor SDA", "type": "I2C"},
            {"component": mcu_name, "pin": "GPIO22 (SCL)", "connected_to": "Default Sensor SCL", "type": "I2C"},
            {"component": mcu_name, "pin": "GPIO25 (PWM)", "connected_to": "Default ESC / Driver Input", "type": "PWM"}
        ])

    return pin_map
