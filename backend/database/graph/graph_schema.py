# Nodes Labels
PROJECT = "Project"
REQUIREMENT = "Requirement"
COMPONENT = "Component"
ELECTRONIC_COMPONENT = "ElectronicComponent"
MECHANICAL_COMPONENT = "MechanicalComponent"
STRUCTURAL_COMPONENT = "StructuralComponent"
CHEMICAL_COMPONENT = "ChemicalComponent"
MICROCONTROLLER = "Microcontroller"
SENSOR = "Sensor"
ACTUATOR = "Actuator"
MOTOR = "Motor"
BATTERY = "Battery"
POWER_RAIL = "PowerRail"
PROTOCOL = "Protocol"
PIN = "Pin"
VENDOR = "Vendor"
MANUFACTURER = "Manufacturer"
DATASHEET = "Datasheet"
RESEARCH_PAPER = "ResearchPaper"
ALGORITHM = "Algorithm"
FAILURE_MODE = "FailureMode"
RECOMMENDATION = "Recommendation"
TIMELINE = "Timeline"
TASK = "Task"
CODE_MODULE = "CodeModule"
AGENT = "Agent"
VALIDATION_RULE = "ValidationRule"
OPTIMIZATION = "Optimization"
EXPORT = "Export"
CITY = "City"
SHIPPING_METHOD = "ShippingMethod"
TOOL = "Tool"
ARMORIQ_POLICY = "ArmorIQPolicy"

# Relationship Types
USES = "USES"
HAS_REQUIREMENT = "HAS_REQUIREMENT"
SUPPORTED_BY = "SUPPORTED_BY"
HAS_BOM = "HAS_BOM"
HAS_TIMELINE = "HAS_TIMELINE"
HAS_TASK = "HAS_TASK"
HAS_EXPORT = "HAS_EXPORT"
GENERATED_BY = "GENERATED_BY"
OPTIMIZED_BY = "OPTIMIZED_BY"
CONNECTED_TO = "CONNECTED_TO"
COMMUNICATES_VIA = "COMMUNICATES_VIA"
POWERED_BY = "POWERED_BY"
HAS_PIN = "HAS_PIN"
HAS_DATASHEET = "HAS_DATASHEET"
MANUFACTURED_BY = "MANUFACTURED_BY"
AVAILABLE_AT = "AVAILABLE_AT"
ALTERNATIVE_TO = "ALTERNATIVE_TO"
HAS_FAILURE_MODE = "HAS_FAILURE_MODE"
REQUIRES = "REQUIRES"
REQUIRES_DRIVER = "REQUIRES_DRIVER"
SELLS = "SELLS"
LOCATED_IN = "LOCATED_IN"
OFFERS = "OFFERS"
CITES = "CITES"
IMPLEMENTS = "IMPLEMENTS"
SUPPORTS = "SUPPORTS"
CONTRADICTS = "CONTRADICTS"
DELEGATES_TO = "DELEGATES_TO"
USES_TOOL = "USES_TOOL"
AUTHORIZED_BY = "AUTHORIZED_BY"

def init_constraints(driver):
    queries = [
        "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Project) REQUIRE p.name IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Component) REQUIRE c.name IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (r:Requirement) REQUIRE r.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (rp:ResearchPaper) REQUIRE rp.title IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (v:Vendor) REQUIRE v.name IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (m:Manufacturer) REQUIRE m.name IS UNIQUE"
    ]
    with driver.session() as session:
        for q in queries:
            try:
                session.run(q)
            except Exception as e:
                import logging
                logging.getLogger("GraphSchema").warning(f"Could not create constraint: {e}")
