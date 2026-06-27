from typing import List, Dict, Any

def search_projects(query: str) -> List[Dict[str, Any]]:
    # Mock data customized based on common engineering requests
    query_lower = query.lower()
    if "solar" in query_lower or "vacuum" in query_lower:
        return [
            {
                "id": "proj_1",
                "title": "SolarVac - High Efficiency Off-Grid Vacuum",
                "source": "GitHub",
                "url": "https://github.com/engineering-labs/solarvac",
                "description": "An open-source design for a solar-powered portable vacuum utilizing lithium iron phosphate batteries and high RPM brushless DC motor.",
                "stars": 342,
                "author": "clean-tech-guru"
            },
            {
                "id": "proj_2",
                "title": "DIY Solar Powered Workshop Dust Collector",
                "source": "Instructables",
                "url": "https://www.instructables.com/diy-solar-dust-collector",
                "description": "Step-by-step assembly of a cyclonic vacuum cleaner powered by a 12V 100W flexible solar panel.",
                "difficulty": "Intermediate",
                "likes": 1205
            },
            {
                "id": "proj_3",
                "title": "Brushless DC Motor Vacuum Control Circuit",
                "source": "YouTube",
                "url": "https://youtube.com/watch?v=blcdVacuumCtrl",
                "description": "Video guide showcasing the wiring of a ESC (Electronic Speed Controller) to a 3-phase BLDC vacuum motor for maximum efficiency.",
                "views": 45000
            }
        ]
    elif "drone" in query_lower or "delivery" in query_lower:
        return [
            {
                "id": "proj_drone_1",
                "title": "OpenDroneDeliver - Heavy Cargo Quadcopter",
                "source": "GitHub",
                "url": "https://github.com/aero-labs/opendronedeliver",
                "description": "Autopilot config and CAD files for a 10kg payload delivery octocopter with automated drop mechanism.",
                "stars": 820,
                "author": "open-aero"
            },
            {
                "id": "proj_drone_2",
                "title": "DIY Autonomous Cargo Release Hook",
                "source": "Instructables",
                "url": "https://www.instructables.com/autonomous-drone-release-mechanism",
                "description": "Complete build tutorial for a servo-actuated landing gear and release latch triggered via Pixhawk PWM outputs.",
                "difficulty": "Advanced",
                "likes": 512
            }
        ]
    else:
        # Generic engineering project
        return [
            {
                "id": "proj_generic_1",
                "title": f"Open-source {query} implementation template",
                "source": "GitHub",
                "url": f"https://github.com/community-eng/{query.replace(' ', '-')}",
                "description": f"A baseline design and reference files for developing a customized {query}.",
                "stars": 42,
                "author": "open-hardware-foundation"
            }
        ]

def fetch_sources(url: str) -> Dict[str, Any]:
    return {
        "url": url,
        "content_markdown": f"# Content from source {url}\n\n## Overview\nThis project details the mechanical construction and electrical diagram. Key components include a high-efficiency controller, custom 3D printed housing, and standard power input connectors.\n\n## Power Specs\n- Peak voltage: 24V DC\n- Max current: 15A\n- Safety fuses: 20A inline",
        "status": "FETCHED"
    }
