import os
import csv
import io
import uuid
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

def export_pdf(data: Dict[str, Any]) -> Dict[str, Any]:
    file_id = f"package_{uuid.uuid4().hex[:8]}"
    filename = f"{file_id}.pdf"
    file_path = os.path.join(EXPORT_DIR, filename)
    
    doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#0f172a'), # slate-900
        spaceAfter=15
    )
    
    section_style = ParagraphStyle(
        'DocSection',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#2563eb'), # blue-600
        spaceBefore=15,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#334155'), # slate-700
        spaceAfter=8
    )
    
    # 1. Header
    story.append(Paragraph("WorkflowGuide AI - Engineering Package", title_style))
    story.append(Paragraph(f"<b>Engineering Concept:</b> {data.get('intent', 'N/A')}", body_style))
    story.append(Paragraph(f"<b>Readiness Score:</b> {data.get('validation', {}).get('readiness_score', 0)}%  |  <b>Risk Score:</b> {data.get('validation', {}).get('risk_score', 0)}%", body_style))
    story.append(Spacer(1, 15))
    
    # 2. Components Table
    story.append(Paragraph("1. Bill of Materials (BOM)", section_style))
    components = data.get("components", [])
    
    table_data = [["Category", "Component", "Est. Cost", "Notes"]]
    for comp in components:
        table_data.append([
            comp.get("category", ""),
            comp.get("name", ""),
            f"${comp.get('cost', 0.0):.2f}",
            comp.get("notes", "")
        ])
        
    t = Table(table_data, colWidths=[100, 180, 60, 180])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')), # blue-900
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))
    
    # 3. Validation Checks
    story.append(Paragraph("2. Feasibility & Validation", section_style))
    checks = data.get("validation", {}).get("validation_checks", [])
    for check in checks:
        story.append(Paragraph(f"<b>[{check.get('status')}] {check.get('check')}</b>: {check.get('details')}", body_style))
        
    story.append(Spacer(1, 15))
    
    # 4. Roadmap
    story.append(Paragraph("3. Execution Roadmap", section_style))
    roadmap = data.get("roadmap", [])
    for r in roadmap:
        story.append(Paragraph(f"<b>Phase {r.get('phase')}: {r.get('title')}</b> ({r.get('duration_days')} days)", body_style))
        story.append(Paragraph(f"<i>Deliverable:</i> {r.get('deliverable')}", body_style))
        story.append(Paragraph(r.get('description', ''), body_style))
        story.append(Spacer(1, 5))
        
    doc.build(story)
    
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
        writer.writerow(["Category", "Component Name", "Estimated Cost", "Notes"])
        for comp in components:
            writer.writerow([
                comp.get("category", ""),
                comp.get("name", ""),
                comp.get("cost", 0.0),
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
    content.append("| Category | Component Name | Estimated Cost | Notes |")
    content.append("| --- | --- | --- | --- |")
    
    for comp in data.get("components", []):
        content.append(f"| {comp.get('category')} | {comp.get('name')} | ${comp.get('cost'):.2f} | {comp.get('notes')} |")
        
    content.append("\n## Validation & Feasibility\n")
    for check in data.get("validation", {}).get("validation_checks", []):
        content.append(f"- **[{check.get('status')}] {check.get('check')}:** {check.get('details')}")
        
    content.append("\n## Execution Roadmap\n")
    for r in data.get("roadmap", []):
        content.append(f"### Phase {r.get('phase')}: {r.get('title')} ({r.get('duration_days')} days)")
        content.append(f"- **Deliverable:** {r.get('deliverable')}")
        content.append(f"- **Description:** {r.get('description')}\n")
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content))
        
    return {
        "filename": filename,
        "url": f"/api/exports/{filename}",
        "status": "SUCCESS"
    }
