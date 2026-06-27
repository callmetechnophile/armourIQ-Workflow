from typing import List, Dict, Any

def search_papers(query: str) -> List[Dict[str, Any]]:
    query_lower = query.lower()
    if "solar" in query_lower or "vacuum" in query_lower:
        return [
            {
                "id": "paper_1",
                "title": "Design Optimization of Photovoltaic-Powered Brushless DC Suction Systems",
                "authors": "A. Rahman, S. Patel, J. Doe",
                "source": "arXiv",
                "url": "https://arxiv.org/abs/2104.09841",
                "publish_year": 2021,
                "citation_count": 28
            },
            {
                "id": "paper_2",
                "title": "A Review of Portable Solar Energy Harvesting Circuits for Low-Power Appliances",
                "authors": "M. Zhang, L. Jenkins",
                "source": "CORE",
                "url": "https://core.ac.uk/reader/82049",
                "publish_year": 2019,
                "citation_count": 64
            }
        ]
    elif "drone" in query_lower or "delivery" in query_lower:
        return [
            {
                "id": "paper_drone_1",
                "title": "Path Optimization and Collision Avoidance for Multi-Agent Drone Delivery Networks",
                "authors": "K. Cho, Y. Tanaka",
                "source": "arXiv",
                "url": "https://arxiv.org/abs/2209.11053",
                "publish_year": 2022,
                "citation_count": 45
            },
            {
                "id": "paper_drone_2",
                "title": "Active Servo Gripper Systems for Package Dropoff on Autonomous UAVs",
                "authors": "H. Schmidt, F. Rossi",
                "source": "IEEE (via OpenAlex)",
                "url": "https://openalex.org/W30193892",
                "publish_year": 2020,
                "citation_count": 19
            }
        ]
    else:
        return [
            {
                "id": "paper_generic_1",
                "title": f"Technical Advancements in Automated {query} Engineering Structures",
                "authors": "Dr. E. Benson, P. Wright",
                "source": "OpenAlex",
                "url": "https://openalex.org/generic-paper-link",
                "publish_year": 2023,
                "citation_count": 3
            }
        ]

def summarize_papers(paper_id: str) -> Dict[str, Any]:
    if "paper_1" in paper_id or "solar" in paper_id:
        return {
            "paper_id": paper_id,
            "title": "Design Optimization of Photovoltaic-Powered Brushless DC Suction Systems",
            "summary": "This study analyzes the power dynamics of matching solar panel arrays with brushless DC motor vacuums. The paper demonstrates that using a Maximum Power Point Tracking (MPPT) charge controller improves suction efficiency by 34% compared to direct-drive configurations under variable irradiance.",
            "conclusions": [
                "Direct connection of solar panels to BLDC motors causes motor stalling under transient cloud cover.",
                "LFP batteries act as a buffer and provide steady voltage profiles for consistent motor RPM."
            ],
            "recommendations": "Integrate an MPPT charge controller (e.g., based on the BQ24650 chip) and a small 12.8V LiFePO4 battery pack."
        }
    elif "drone" in paper_id:
        return {
            "paper_id": paper_id,
            "title": "Path Optimization and Collision Avoidance for Multi-Agent Drone Delivery Networks",
            "summary": "This paper presents algorithms for autonomous route planning of quadcopters carrying packages. It demonstrates that dynamic boundary safety margins reduce collision rates to nearly 0% while optimizing battery consumption by choosing altitudes with minimum headwind.",
            "conclusions": [
                "Headwinds increase power consumption by up to 45% during forward flight.",
                "Geofencing and fail-safe return-to-home (RTH) procedures must run on a secondary hardware controller."
            ],
            "recommendations": "Incorporate Pixhawk flight controller with dual GPS redundancy and an auxiliary Raspberry Pi for companion path calculation."
        }
    else:
        return {
            "paper_id": paper_id,
            "title": "Technical Advancements in Automated Engineering Structures",
            "summary": "Presents core mathematical modeling for load-bearing and energy conversion structures. Suggests modular component integration to reduce single-point failure rates.",
            "conclusions": [
                "Modular structural units reduce maintenance time.",
                "Standard power rails ease component swap operations."
            ],
            "recommendations": "Ensure all power distributions are modularized and fused."
        }
