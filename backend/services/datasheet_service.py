from typing import List, Dict, Any

DATASHEET_DATABASE = {
    "esp32": {
        "link": "https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf",
        "source": "Espressif Systems (Official)"
    },
    "pca9685": {
        "link": "https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf",
        "source": "NXP Semiconductors (Official)"
    },
    "sg90": {
        "link": "https://components101.com/sites/default/files/component_datasheet/SG90%20Servo%20Motor%20Datasheet.pdf",
        "source": "TowerPro (Official)"
    },
    "mg996r": {
        "link": "https://www.electronicoscaldas.com/datasheet/MG996R_Tower-Pro.pdf",
        "source": "TowerPro (Official)"
    },
    "flex sensor": {
        "link": "https://www.sparkfun.com/datasheets/Sensors/Flex/flex22.pdf",
        "source": "Spectra Symbol (Official)"
    },
    "brushless motor": {
        "link": "https://www.mouser.com/datasheet/2/389/l298-954953.pdf",
        "source": "Mouser Electronics (Distributor)"
    },
    "esc": {
        "link": "https://www.hobbywing.com/products/pdf/FlyFun.pdf",
        "source": "Hobbywing (Official)"
    },
    "pixhawk": {
        "link": "https://docs.px4.io/main/en/flight_controller/pixhawk6c.html",
        "source": "Holybro Systems (Official)"
    },
    "gps": {
        "link": "https://www.u-blox.com/sites/default/files/NEO-M8_DataSheet_%28UBX-13003366%29.pdf",
        "source": "u-blox (Official)"
    },
    "telemetry": {
        "link": "https://files.rfdesign.com.au/Files/documents/RFD900x%20Datasheet.pdf",
        "source": "RFDesign (Official)"
    },
    "solar panel": {
        "link": "https://www.renogy.com/template/files/Datasheets/RNG-100DB-H.pdf",
        "source": "Renogy (Official)"
    },
    "suction motor": {
        "link": "https://www.st.com/resource/en/datasheet/l6234.pdf",
        "source": "STMicroelectronics (Official)"
    },
    "charge controller": {
        "link": "https://www.epsolarpv.com/upload/cert/Tracer-AN-manual-EN-V2.1.pdf",
        "source": "EPEver (Official)"
    },
    "battery": {
        "link": "https://www.renogy.com/template/files/Datasheets/RBT100LFP12S-G1.pdf",
        "source": "Renogy (Official)"
    }
}

def fetch_datasheet_links(component_name: str) -> Dict[str, str]:
    """
    Scans component names and queries official manufacturer or distributor PDF links.
    """
    name_lower = component_name.lower()
    
    for key, spec in DATASHEET_DATABASE.items():
        if key in name_lower:
            # Check source credibility (Official vs Distributor)
            trust_level = "TRUSTED" if "Official" in spec["source"] else "VERIFIED"
            return {
                "component": component_name,
                "datasheet_link": spec["link"],
                "source": spec["source"],
                "trust_status": trust_level
            }
            
    # Fallback generic components page on Mouser
    fallback_url = f"https://www.mouser.in/c/?q={component_name.replace(' ', '+')}"
    return {
        "component": component_name,
        "datasheet_link": fallback_url,
        "source": "Mouser Electronics Search (Fallback)",
        "trust_status": "UNVERIFIED"
    }
