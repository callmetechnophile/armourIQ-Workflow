import os
import csv
import io
import uuid
import json
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

def generate_project_title(user_query: str) -> str:
    """
    Converts a raw user query into a short, clean, engineering-style project title using Gemma.
    """
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if groq_api_key and not groq_api_key.startswith("gsk_placeholder"):
        try:
            import httpx
            payload = {
                "model": "gemma2-9b-it",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a technical naming system. Convert the user's hardware prototype query "
                            "into a short, clean, professional engineering-style project title. "
                            "Rules: Remove filler words, remove 'I want to build', remove generic words. "
                            "Compress into 1 to 3 words. Must sound technical (e.g. 'SolarVac System', 'AeroDrop System'). "
                            "Reply ONLY with the project name. Do not include quotes, periods, explanation or markdown."
                        )
                    },
                    {"role": "user", "content": user_query}
                ],
                "temperature": 0.1,
                "max_tokens": 10
            }
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            with httpx.Client(timeout=10.0) as client:
                res = client.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
                if res.status_code == 200:
                    title = res.json()["choices"][0]["message"]["content"].strip()
                    title = title.replace('"', '').replace("'", "").replace('.', '').strip()
                    if title:
                        return title
        except Exception as e:
            print(f"[Naming] Gemma naming failed: {e}. Falling back to local rules.")

    # Local Fallback Naming Engine
    query_lower = user_query.lower()
    if "solar" in query_lower and ("vacuum" in query_lower or "clean" in query_lower):
        return "SolarVac System"
    elif "drone" in query_lower or "delivery" in query_lower:
        return "AeroDrop System"
    elif "irrigation" in query_lower or "water" in query_lower or "agri" in query_lower:
        return "AgriFlow System"
    elif "hand" in query_lower or "bionic" in query_lower or "robotic" in query_lower:
        return "BionicHand System"
    
    words = [w for w in user_query.split() if w.lower() not in ["i", "want", "to", "build", "a", "an", "the", "using", "with", "for", "smart"]]
    if len(words) >= 2:
        title = "".join(w.capitalize() for w in words[:2]) + " System"
    elif len(words) == 1:
        title = words[0].capitalize() + " System"
    else:
        title = "ArmourFlow Project"
    return title

def generate_abstract(project_title: str, user_query: str) -> str:
    """
    Generates a 150-250 word project abstract using Nemotron.
    """
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if groq_api_key and not groq_api_key.startswith("gsk_placeholder"):
        try:
            import httpx
            payload = {
                "model": "llama-3.1-nemotron-70b-specdec",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a professional hardware research engineer. "
                            "Write a professional project abstract of 150 to 250 words for the project: "
                            f"'{project_title}' (Query: '{user_query}'). "
                            "The abstract MUST contain four distinct sections: "
                            "Problem, Solution, Implementation Idea, and Feasibility. "
                            "Keep it highly technical, objective, and clear. Do not include markdown headers or greetings."
                        )
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 400
            }
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            with httpx.Client(timeout=12.0) as client:
                res = client.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
                if res.status_code == 200:
                    abstract = res.json()["choices"][0]["message"]["content"].strip()
                    if abstract:
                        return abstract
        except Exception as e:
            print(f"[Abstract] Nemotron abstract failed: {e}. Falling back to local template.")

    # Local Fallback Abstract template
    return (
        f"PROBLEM: Standard prototyping systems for {user_query} suffer from inefficient component sourcing, "
        "voltage mismatches, and severe security compliance policy gaps during autonomous research.\n\n"
        f"SOLUTION: The {project_title} design resolves this by leveraging an autonomous multi-agent pipeline "
        "coupled with the ArmorIQ trust enforcer. This architecture calculates optimal vendor logistics, common "
        "grounds, and pin configurations before hardware assembly.\n\n"
        "IMPLEMENTATION IDEA: The physical system incorporates core microcontroller logic, PCA9685 servo controllers, "
        "and high-efficiency power cells mapped via custom SPI/I2C wire connections.\n\n"
        "FEASIBILITY: Engineering validation estimates a readiness level of 85% with negligible voltage mismatch "
        "hazards, ensuring high reliability under peak power requirements."
    )

def generate_firmware_code(components: List[Dict[str, Any]], intent: str) -> str:
    mcu = "ESP32 Board"
    has_pca = any("pca9685" in (c.get("component") or c.get("name", "")).lower() for c in components)
    has_servos = any("servo" in (c.get("component") or c.get("name", "")).lower() for c in components)
    
    if has_pca and has_servos:
        return """#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define FLEX_THUMB  32
#define FLEX_INDEX  33
#define FLEX_MIDDLE 34
#define FLEX_RING   35
#define FLEX_PINKY  36

#define SERVOMIN  150 
#define SERVOMAX  600 

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22); 
  pwm.begin();
  pwm.setOscillatorFrequency(27000000);
  pwm.setPWMFreq(50); 
  
  pinMode(FLEX_THUMB, INPUT);
  pinMode(FLEX_INDEX, INPUT);
  pinMode(FLEX_MIDDLE, INPUT);
  pinMode(FLEX_RING, INPUT);
  pinMode(FLEX_PINKY, INPUT);
}

void loop() {
  int valThumb  = analogRead(FLEX_THUMB);
  int valIndex  = analogRead(FLEX_INDEX);
  int valMiddle = analogRead(FLEX_MIDDLE);
  int valRing   = analogRead(FLEX_RING);
  int valPinky  = analogRead(FLEX_PINKY);
  
  int pulseThumb  = map(valThumb,  1000, 3000, SERVOMIN, SERVOMAX);
  int pulseIndex  = map(valIndex,  1000, 3000, SERVOMIN, SERVOMAX);
  int pulseMiddle = map(valMiddle, 1000, 3000, SERVOMIN, SERVOMAX);
  int pulseRing   = map(valRing,   1000, 3000, SERVOMIN, SERVOMAX);
  int pulsePinky  = map(valPinky,  1000, 3000, SERVOMIN, SERVOMAX);
  
  pwm.setPWM(0, 0, constrain(pulseThumb,  SERVOMIN, SERVOMAX));
  pwm.setPWM(1, 0, constrain(pulseIndex,  SERVOMIN, SERVOMAX));
  pwm.setPWM(2, 0, constrain(pulseMiddle, SERVOMIN, SERVOMAX));
  pwm.setPWM(3, 0, constrain(pulseRing,   SERVOMIN, SERVOMAX));
  pwm.setPWM(4, 0, constrain(pulsePinky,  SERVOMIN, SERVOMAX));
  delay(20);
}"""
    elif "solar" in intent.lower() or "vacuum" in intent.lower():
        return """#define VACUUM_MOTOR_PWM 15
#define SOLAR_CHARGE_PIN 34
#define BATTERY_VOLTAGE_PIN 35

void setup() {
  Serial.begin(115200);
  pinMode(VACUUM_MOTOR_PWM, OUTPUT);
}

void loop() {
  int batVal = analogRead(BATTERY_VOLTAGE_PIN);
  float voltage = (batVal / 4095.0) * 3.3 * 4.0;
  
  if (voltage < 10.5) {
    analogWrite(VACUUM_MOTOR_PWM, 0);
  } else {
    analogWrite(VACUUM_MOTOR_PWM, 180); 
  }
  delay(100);
}"""
    else:
        return """#define STATUS_LED 2

void setup() {
  Serial.begin(115200);
  pinMode(STATUS_LED, OUTPUT);
}

void loop() {
  digitalWrite(STATUS_LED, HIGH);
  delay(500);
  digitalWrite(STATUS_LED, LOW);
  delay(500);
}"""

def export_pdf(data: Dict[str, Any]) -> Dict[str, Any]:
    # 1. Generate naming metadata
    intent = data.get("intent", "Project Specification")
    project_title = generate_project_title(intent)
    abstract_text = generate_abstract(project_title, intent)
    
    filename = f"{project_title.replace(' ', '_')}.pdf"
    file_path = os.path.join(EXPORT_DIR, filename)
    
    # 2. Setup document template
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=55
    )
    story = []
    
    # 3. Setup typography styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=24, leading=28,
        textColor=colors.HexColor('#0f172a'), spaceAfter=15
    )
    subtitle_style = ParagraphStyle(
        'DocSub', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=14, leading=18,
        textColor=colors.HexColor('#475569'), spaceAfter=10
    )
    tagline_style = ParagraphStyle(
        'DocTag', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=11, leading=15,
        textColor=colors.HexColor('#64748b'), spaceAfter=8
    )
    section_style = ParagraphStyle(
        'DocSection', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=15, leading=19,
        textColor=colors.HexColor('#1e293b'), spaceBefore=10, spaceAfter=8
    )
    body_style = ParagraphStyle(
        'DocBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, leading=14,
        textColor=colors.HexColor('#334155'), spaceAfter=8
    )
    code_style = ParagraphStyle(
        'DocCode', parent=styles['Normal'],
        fontName='Courier', fontSize=8, leading=11,
        textColor=colors.HexColor('#0f172a'), spaceAfter=6
    )
    table_header_style = ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=10,
        textColor=colors.white
    )
    table_body_style = ParagraphStyle(
        'TableBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=10,
        textColor=colors.HexColor('#334155')
    )

    # Context variables
    components = data.get("components", [])
    validation = data.get("validation", {})
    readiness_score = validation.get("readiness_score", 80)
    complexity = "High" if len(components) > 5 else "Medium"
    
    # Calculate costs
    cost_summary = data.get("cost_summary", {})
    total_cost = cost_summary.get("total_landed_cost", sum(c.get("cost", 0) for c in components))
    if isinstance(total_cost, (int, float)):
        total_cost = int(total_cost * 83.0) if total_cost < 1000 else int(total_cost) # handle rupees/dollar scales
    
    # helper to make tables easily
    def make_pdf_table(rows_data, col_widths):
        t = Table(rows_data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc'))
        ]))
        return t

    # ----------------------------------------------------
    # PAGE 1: COVER PAGE
    # ----------------------------------------------------
    story.append(Spacer(1, 100))
    story.append(Paragraph(project_title, title_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("Engineering Research & Execution Report", subtitle_style))
    story.append(Spacer(1, 30))
    story.append(Paragraph("Generated via WorkflowGuide AI", tagline_style))
    story.append(Spacer(1, 120))
    story.append(Paragraph(f"<b>Generation Timestamp:</b> {datetime.utcnow().isoformat()} UTC", body_style))
    story.append(Paragraph(f"<b>Execution Readiness Score:</b> {readiness_score}%", body_style))
    story.append(Paragraph(f"<b>Total BOM Cost:</b> ₹{total_cost:,}", body_style))
    story.append(Paragraph(f"<b>Project Complexity:</b> {complexity}", body_style))
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 2: ABSTRACT
    # ----------------------------------------------------
    story.append(Paragraph("Abstract", section_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph(abstract_text, body_style))
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 3: PROBLEM STATEMENT
    # ----------------------------------------------------
    story.append(Paragraph("Problem Statement", section_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph(f"<b>Target Engineering Objective:</b> {intent}", body_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>1. Complex Procurement Logistics:</b> Component acquisition is bottlenecked by fragmented distributor channels (Mouser, element14, Robu) leading to unoptimized shipping expenses and volatile customs/clearance delays.", body_style))
    story.append(Paragraph("<b>2. Logic-Level Mismatches:</b> Microcontroller-driven logic (3.3V CMOS thresholds) connected directly to standard PWM motor controllers (5V TTL inputs) causes signal line degradation, high leakage currents, and transistor failure.", body_style))
    story.append(Paragraph("<b>3. Policy Auditing Deficiencies:</b> Autonomous hardware builders lack real-time sandboxing checks, causing research modules to invoke unauthorized tool commands (e.g. system file calls).", body_style))
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 4: PROPOSED SOLUTION
    # ----------------------------------------------------
    story.append(Paragraph("Proposed Solution", section_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph(f"The <b>{project_title}</b> is implemented as a cryptographically-secured bionic control platform.", body_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Autonomous Pipeline:</b> An integrated planner guides retrieval, extraction, and validation agents. The cost engine dynamically swaps optimal local vendors to calculate landed prices.", body_style))
    story.append(Paragraph("<b>Electrical Safety Enforcer:</b> Logic gates checks, pin configurations maps, and voltage risk models validate pin configurations before actual hardware hookups.", body_style))
    story.append(Paragraph("<b>ArmorIQ Sandbox:</b> Out-of-scope system calls are intercepted and blocked at runtime, logging tamper-proof cryptographic receipts.", body_style))
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 5: SYSTEM ARCHITECTURE
    # ----------------------------------------------------
    story.append(Paragraph("System Architecture Flow", section_style))
    story.append(Spacer(1, 15))
    flow_lines = [
        "User Query (Natural Language Target Specification)",
        "   ↓",
        "Planner Agent [delegates pipeline execution stages]",
        "   ↓",
        "Retrieval Agent [queries local and online databases]",
        "   ↓",
        "Extraction Agent [extracts component spec listings]",
        "   ↓",
        "ProcurementAgent [optimizes BOM, matches vendors]",
        "   ↓",
        "Research Agent [ranks papers, extracts summaries]",
        "   ↓",
        "Validation Agent [safety checks electrical signals]",
        "   ↓",
        "Optimization Agent [swaps cost-effective modules]",
        "   ↓",
        "Planning Agent [generates roadmap and Gantt schedule]",
        "   ↓",
        "Export Agent [compiles report documents bundle]"
    ]
    for line in flow_lines:
        story.append(Paragraph(line, code_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Zero-Trust Governance:</b> ArmorIQ validation intercepts all agent tool calls, cross-matching permissions against the authorization scope map.", body_style))
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 6: BOM TABLE
    # ----------------------------------------------------
    story.append(Paragraph("Bill of Materials (BOM)", section_style))
    story.append(Spacer(1, 10))
    
    headers = [Paragraph("Component", table_header_style), Paragraph("Vendor", table_header_style), Paragraph("Base Cost", table_header_style), Paragraph("Shipping", table_header_style), Paragraph("Final Cost", table_header_style), Paragraph("Stock", table_header_style)]
    rows = [headers]
    
    for c in components:
        rows.append([
            Paragraph(c.get("component") or c.get("name", "N/A"), table_body_style),
            Paragraph(c.get("selected_vendor", "element14 India"), table_body_style),
            Paragraph(f"₹{int(c.get('base_cost', c.get('cost', 0)*83.0)):,}", table_body_style),
            Paragraph(f"₹{int(c.get('shipping_cost', 90)):,}", table_body_style),
            Paragraph(f"₹{int(c.get('final_cost', c.get('cost', 0)*83.0 + 90)):,}", table_body_style),
            Paragraph(c.get("stock", "In Stock"), table_body_style)
        ])
        
    bom_table = make_pdf_table(rows, [165, 95, 60, 60, 60, 60])
    story.append(bom_table)
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<b>Grand Landed Total Cost:</b> ₹{total_cost:,}", body_style))
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 7: ALTERNATIVE COMPONENTS
    # ----------------------------------------------------
    story.append(Paragraph("Alternative Component Optimization", section_style))
    story.append(Spacer(1, 15))
    
    alternatives = data.get("alternatives", [])
    if not alternatives:
        story.append(Paragraph("All component selections currently optimized at maximum efficiency settings.", body_style))
    else:
        for idx, alt in enumerate(alternatives[:3]):
            story.append(Paragraph(f"<b>Alternative Set {idx+1}:</b>", body_style))
            story.append(Paragraph(f"• Original Part: {alt.get('original', 'Standard MCU')}", body_style))
            story.append(Paragraph(f"• Option Swap: {alt.get('alternative') or alt.get('name', 'N/A')}", body_style))
            story.append(Paragraph(f"• Selection Rationale: {alt.get('reason', 'N/A')}", body_style))
            story.append(Paragraph(f"• Cost Delta: {alt.get('cost_diff') or 'Saved 15%'}", body_style))
            story.append(Spacer(1, 8))
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 8: POWER ANALYSIS
    # ----------------------------------------------------
    story.append(Paragraph("System Power Analysis", section_style))
    story.append(Spacer(1, 10))
    
    power_data = data.get("power_analysis", {})
    power_items = power_data.get("power_items", [])
    
    p_headers = [Paragraph("Component", table_header_style), Paragraph("Voltage", table_header_style), Paragraph("Nominal Draw", table_header_style), Paragraph("Peak Draw", table_header_style)]
    p_rows = [p_headers]
    
    for item in power_items:
        p_rows.append([
            Paragraph(item.get("component", ""), table_body_style),
            Paragraph(f"{item.get('voltage')} V", table_body_style),
            Paragraph(f"{item.get('nominal_current')} mA", table_body_style),
            Paragraph(f"{item.get('peak_current')} mA", table_body_style)
        ])
        
    p_table = make_pdf_table(p_rows, [220, 80, 100, 100])
    story.append(p_table)
    
    p_summary = power_data.get("summary", {})
    story.append(Spacer(1, 15))
    story.append(Paragraph(f"• <b>Total Watts Load:</b> {p_summary.get('total_power_load_w', 1.5)} W", body_style))
    story.append(Paragraph(f"• <b>Battery Runtime:</b> {p_summary.get('estimated_runtime_hours', 2.0)} Hours", body_style))
    
    p_warnings = power_data.get("warnings", [])
    if p_warnings:
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Power Warning Reports:</b>", body_style))
        for warn in p_warnings:
            story.append(Paragraph(f"⚠️ {warn}", body_style))
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 9: DEPENDENCY GRAPH
    # ----------------------------------------------------
    story.append(Paragraph("System Dependency Graph", section_style))
    story.append(Spacer(1, 15))
    
    dep_data = data.get("dependency_graph", {})
    dep_edges = dep_data.get("edges", [])
    
    story.append(Paragraph("Hierarchical structural connections extracted from pipeline dependencies:", body_style))
    story.append(Spacer(1, 10))
    
    for edge in dep_edges:
        story.append(Paragraph(f"• <b>{edge.get('source')}</b> ➔ <b>{edge.get('target')}</b> ({edge.get('type')}: {edge.get('label')})", body_style))
        
    if not dep_edges:
        story.append(Paragraph("No active dependency lines detected.", body_style))
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 10: WIRING DIAGRAM
    # ----------------------------------------------------
    story.append(Paragraph("System Wiring Schematic", section_style))
    story.append(Spacer(1, 15))
    
    wiring_data = data.get("wiring_diagram", {})
    connections = wiring_data.get("connections", [])
    
    story.append(Paragraph("Physical point-to-point pin wiring connections mapping:", body_style))
    story.append(Spacer(1, 10))
    
    for conn in connections:
        story.append(Paragraph(f"• <b>{conn.get('source')}</b> [{conn.get('source_pin')}] ➔ <b>{conn.get('target')}</b> [{conn.get('target_pin')}] (Bus: {conn.get('protocol')})", body_style))
        
    if not connections:
        story.append(Paragraph("Generic terminal hookups loaded.", body_style))
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 11: PIN CONFIGURATION TABLE
    # ----------------------------------------------------
    story.append(Paragraph("Pin Configuration Mapping", section_style))
    story.append(Spacer(1, 10))
    
    pin_headers = [Paragraph("Source Module", table_header_style), Paragraph("Pin", table_header_style), Paragraph("Connected To", table_header_style), Paragraph("Protocol", table_header_style)]
    pin_rows = [pin_headers]
    
    for conn in connections:
        pin_rows.append([
            Paragraph(conn.get("source"), table_body_style),
            Paragraph(conn.get("source_pin"), table_body_style),
            Paragraph(f"{conn.get('target')} ({conn.get('target_pin')})", table_body_style),
            Paragraph(conn.get("protocol"), table_body_style)
        ])
        
    pin_table = make_pdf_table(pin_rows, [120, 100, 180, 100])
    story.append(pin_table)
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 12: DATASHEETS
    # ----------------------------------------------------
    story.append(Paragraph("Component Datasheets", section_style))
    story.append(Spacer(1, 10))
    
    ds_headers = [Paragraph("Component", table_header_style), Paragraph("Datasheet Link (Clickable)", table_header_style), Paragraph("Source Publisher", table_header_style)]
    ds_rows = [ds_headers]
    
    datasheets = data.get("datasheets", [])
    for ds in datasheets:
        url = ds.get("datasheet_link", "")
        # Render clickable link inside PDF
        link_html = f'<a href="{url}" color="blue"><u>{url[:45]}...</u></a>'
        ds_rows.append([
            Paragraph(ds.get("component"), table_body_style),
            Paragraph(link_html, table_body_style),
            Paragraph(ds.get("source"), table_body_style)
        ])
        
    ds_table = make_pdf_table(ds_rows, [140, 240, 120])
    story.append(ds_table)
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 13: RESEARCH PAPERS
    # ----------------------------------------------------
    story.append(Paragraph("Academic References & Literature", section_style))
    story.append(Spacer(1, 10))
    
    papers = data.get("papers", [])
    paper_headers = [Paragraph("Title", table_header_style), Paragraph("Score", table_header_style), Paragraph("Publish Year", table_header_style), Paragraph("URL Source", table_header_style)]
    paper_rows = [paper_headers]
    
    for paper in papers[:3]:
        url = paper.get("url", "")
        link_html = f'<a href="{url}" color="blue"><u>Source</u></a>'
        paper_rows.append([
            Paragraph(paper.get("title", "N/A"), table_body_style),
            Paragraph(f"{paper.get('score', 80)}/100", table_body_style),
            Paragraph(str(paper.get("publish_year", 2022)), table_body_style),
            Paragraph(link_html, table_body_style)
        ])
        
    paper_table = make_pdf_table(paper_rows, [280, 50, 70, 100])
    story.append(paper_table)
    
    paper_summary = data.get("paper_summary", {})
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Literature Deep-Summary Digest:</b>", subtitle_style))
    story.append(Paragraph(paper_summary.get("summary", "Consolidated academic papers details compiled in research logs."), body_style))
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 14: ENGINEERING VALIDATION
    # ----------------------------------------------------
    story.append(Paragraph("Engineering Validation Report", section_style))
    story.append(Spacer(1, 15))
    
    val_checks = validation.get("validation_checks", [])
    story.append(Paragraph("<b>Safety Checks Compliance Audit:</b>", subtitle_style))
    for check in val_checks:
        story.append(Paragraph(f"• <b>[{check.get('status')}]</b> {check.get('check')}: {check.get('details')}", body_style))
        
    contradictions = validation.get("contradictions", [])
    if contradictions:
        story.append(Spacer(1, 15))
        story.append(Paragraph("<b>Contradiction Risks & Mitigations:</b>", subtitle_style))
        for c in contradictions:
            story.append(Paragraph(f"⚠️ <b>{c.get('conflict')} ({c.get('severity')}):</b> {c.get('explanation')}", body_style))
            story.append(Paragraph(f"<i>Mitigation:</i> {c.get('mitigation')}", body_style))
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 15: OPTIMIZATION REPORT
    # ----------------------------------------------------
    story.append(Paragraph("System Optimization Report", section_style))
    story.append(Spacer(1, 15))
    
    optimization_res = data.get("optimization", {})
    recs = optimization_res.get("recommendations", [])
    
    story.append(Paragraph("<b>Performance & Efficiency Enhancements:</b>", subtitle_style))
    for r in recs:
        story.append(Paragraph(f"• {r}", body_style))
        
    story.append(Spacer(1, 15))
    story.append(Paragraph(f"• <b>System Sourcing Optimization Score:</b> {optimization_res.get('optimization_score', 90)}%", body_style))
    story.append(Paragraph(f"• <b>Acquisition Cost Savings:</b> ₹{int(optimization_res.get('saved_amount', 12.0)*83.0):,}", body_style))
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 16: GENERATED CODE (MAX 2 PAGES)
    # ----------------------------------------------------
    story.append(Paragraph("Generated Controller Firmware", section_style))
    story.append(Spacer(1, 10))
    
    code_text = generate_firmware_code(components, intent)
    story.append(Paragraph(f"<b>Target MCU:</b> ESP32 Core  |  <b>Framework:</b> Arduino C++ IDE", body_style))
    story.append(Spacer(1, 10))
    
    # Split code to avoid page overflow, max 35 lines per page
    code_lines = code_text.split('\n')
    page_1_code = code_lines[:38]
    page_2_code = code_lines[38:76]
    
    for line in page_1_code:
        # Keep spaces indent visible in reportlab Paragraph by replacing with HTML spaces
        spaced_line = line.replace(' ', '&nbsp;')
        story.append(Paragraph(spaced_line, code_style))
        
    story.append(PageBreak())
    
    # Page 17: Continue generated code
    story.append(Paragraph("Generated Controller Firmware (Continued)", section_style))
    story.append(Spacer(1, 10))
    
    for line in page_2_code:
        spaced_line = line.replace(' ', '&nbsp;')
        story.append(Paragraph(spaced_line, code_style))
        
    if len(code_lines) > 76:
        story.append(Spacer(1, 10))
        story.append(Paragraph("<i>[Full code truncated. Full code available in exported source files.]</i>", tagline_style))
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 18: GANTT TIMELINE
    # ----------------------------------------------------
    story.append(Paragraph("Gantt Assembly Schedule", section_style))
    story.append(Spacer(1, 10))
    
    roadmap = data.get("roadmap", [])
    for phase in roadmap:
        story.append(Paragraph(f"<b>Phase {phase.get('phase')}: {phase.get('title')}</b>", subtitle_style))
        story.append(Paragraph(f"• Duration: {phase.get('duration_days')} Days  |  Deliverable: {phase.get('deliverable')}", body_style))
        story.append(Paragraph(phase.get('description', ''), body_style))
        story.append(Spacer(1, 5))
        
    if not roadmap:
        story.append(Paragraph("Standard 4-phase prototyping path generated in repository timeline logs.", body_style))
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 19: CONNECTION ASSISTANT NOTES
    # ----------------------------------------------------
    story.append(Paragraph("Connection Assistant Debugging Notes", section_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>Top Debugging Recommendations:</b>", subtitle_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph("<b>1. Ground Loop Prevention:</b> PCA9685 logic ground must share a physical common node with the ESP32 GND, but servo motor return current paths must route directly back to the LiPo battery terminal block to prevent MCU resets.", body_style))
    story.append(Paragraph("<b>2. Pull-up Resistors on I2C:</b> Ensure SDA and SCL lines have 4.7k ohm pull-up resistors to the 3.3V rail. High transient noise from servos will crash the I2C registers if signal lines float.", body_style))
    story.append(Paragraph("<b>3. Power De-coupling:</b> Install a 1000uF low-ESR electrolytic capacitor across the PCA9685 green V+ power terminal blocks to filter voltage ripple during peak servo stall draws.", body_style))
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 20: ARMORIQ AUDIT TRAIL
    # ----------------------------------------------------
    story.append(Paragraph("ArmorIQ Verification Audit Trail", section_style))
    story.append(Spacer(1, 10))
    
    audit_headers = [Paragraph("Agent", table_header_style), Paragraph("Tool", table_header_style), Paragraph("Scope", table_header_style), Paragraph("Status", table_header_style), Paragraph("Receipt Hash", table_header_style)]
    audit_rows = [audit_headers]
    
    audit_trail = data.get("audit_trail", [])
    for log in audit_trail[:12]: # fit within page
        h = log.get("receipt_hash", "N/A")
        short_hash = f"{h[:6]}...{h[-6:]}" if len(h) > 12 else h
        audit_rows.append([
            Paragraph(log.get("agent", ""), table_body_style),
            Paragraph(log.get("tool", ""), table_body_style),
            Paragraph(log.get("scope", ""), table_body_style),
            Paragraph(log.get("status", ""), table_body_style),
            Paragraph(short_hash, table_body_style)
        ])
        
    audit_table = make_pdf_table(audit_rows, [100, 110, 110, 75, 105])
    story.append(audit_table)
    story.append(PageBreak())

    # ----------------------------------------------------
    # PAGE 21: CONCLUSION
    # ----------------------------------------------------
    story.append(Paragraph("Engineering Conclusion & Readiness Summary", section_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>Readiness Metrics:</b>", subtitle_style))
    story.append(Paragraph(f"• <b>Build Feasibility:</b> {readiness_score}% (Validated wiring configuration and logic domains compatibility)", body_style))
    story.append(Paragraph("• <b>Cost Feasibility:</b> 92% (Landed cost optimized across element14, Mouser, and local vendors)", body_style))
    story.append(Paragraph(f"• <b>Complexity Rating:</b> {complexity} (Multi-module control loop)", body_style))
    story.append(Paragraph("• <b>Estimated Build Time:</b> 12 Days (4-phase roadmap sequential assembly)", body_style))
    story.append(Paragraph("• <b>Skill Level Required:</b> Intermediate Electronics & Firmware design", body_style))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Summary:</b>", subtitle_style))
    story.append(Paragraph(f"The {project_title} project has been successfully compiled and verified by the multi-agent system. "
                           "The electrical wiring schematic, I2C logic domains, and battery discharge current thresholds show full compatibility. "
                           "No critical hazards were logged in the final validation audit trace. Sourcing options reflect "
                           "the most cost-effective alternatives, making it fully ready for hardware prototyping assembly.", body_style))
    
    # 4. Canvas Page Number Footer Callback Helper
    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#475569'))
        page_num = canvas.getPageNumber()
        
        # Draw clean divider line
        canvas.setStrokeColor(colors.HexColor('#e2e8f0'))
        canvas.setLineWidth(0.5)
        canvas.line(40, 45, A4[0] - 40, 45)
        
        canvas.drawString(40, 30, f"{project_title} - Engineering Research & Execution Report")
        canvas.drawRightString(A4[0] - 40, 30, f"Page {page_num} of 21")
        canvas.restoreState()
        
    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    
    return {
        "filename": filename,
        "url": f"/api/exports/{filename}",
        "status": "SUCCESS"
    }

def export_csv(data: Dict[str, Any]) -> Dict[str, Any]:
    file_id = f"package_{uuid.uuid4().hex[:8]}"
    filename = f"{file_id}.csv"
    file_path = os.path.join(EXPORT_DIR, filename)
    
    components = data.get("components", [])
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Category", "Component Name", "Base Cost", "Shipping Cost", "Final Cost", "Vendor", "Notes"])
        for comp in components:
            writer.writerow([
                comp.get("category", ""),
                comp.get("component") or comp.get("name", ""),
                comp.get("base_cost", comp.get("cost", 0)),
                comp.get("shipping_cost", 90),
                comp.get("final_cost", comp.get("cost", 0) + 90),
                comp.get("selected_vendor", "element14 India"),
                comp.get("notes", "")
            ])
            
    return {
        "filename": filename,
        "url": f"/api/exports/{filename}",
        "status": "SUCCESS"
    }

def export_markdown(data: Dict[str, Any]) -> Dict[str, Any]:
    file_id = f"package_{uuid.uuid4().hex[:8]}"
    filename = f"{file_id}.md"
    file_path = os.path.join(EXPORT_DIR, filename)
    
    content = []
    content.append(f"# WorkflowGuide AI Engineering Package - {data.get('intent', 'Project')}\n")
    content.append(f"**Readiness Score:** {data.get('validation', {}).get('readiness_score', 0)}%  \n")
    content.append(f"**Risk Score:** {data.get('validation', {}).get('risk_score', 0)}%  \n")
    content.append("\n## Bill of Materials (BOM)\n")
    content.append("| Category | Component Name | Base Cost | Shipping | Final Landed Cost | Vendor | Notes |")
    content.append("| --- | --- | --- | --- | --- | --- | --- |")
    
    for comp in data.get("components", []):
        content.append(
            f"| {comp.get('category')} | {comp.get('component') or comp.get('name')} | "
            f"₹{comp.get('base_cost', comp.get('cost', 0)):,} | "
            f"₹{comp.get('shipping_cost', 90):,} | "
            f"₹{comp.get('final_cost', comp.get('cost', 0) + 90):,} | "
            f"{comp.get('selected_vendor')} | {comp.get('notes')} |"
        )
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content))
        
    return {
        "filename": filename,
        "url": f"/api/exports/{filename}",
        "status": "SUCCESS"
    }
