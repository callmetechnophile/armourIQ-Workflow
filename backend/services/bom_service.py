import os
import csv
import json
import uuid
from typing import List, Dict, Any

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

def export_bom(components: List[Dict[str, Any]], cost_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Exports the Bill of Materials (BOM) with quantities, categories, vendors, prices,
    stock status, alternatives, and totals into CSV, JSON, and Markdown formats.
    Saves files to the backend/exports/ directory and returns download URLs.
    """
    file_id = str(uuid.uuid4())[:8]
    
    # 1. Compile BOM items with default values (Qty: 1, Stock: In Stock, Vendor: standard)
    bom_items = []
    conversion_rate = 83
    
    for comp in components:
        name = comp.get("name", "")
        cost_usd = float(comp.get("cost", 0.0))
        cost_inr = int(cost_usd * conversion_rate)
        category = comp.get("category", "")
        
        # Hardcode some vendors for realistic details
        vendor = "Robokits India" if "motor" in name.lower() or "esc" in name.lower() else "Amazon India"
        
        # Retrieve some alternatives (cheaper or equivalent)
        from backend.services.alternative_service import find_alternatives
        alts = find_alternatives(name)
        alt_names = ", ".join([a["name"] for a in alts]) if alts else "None"
        
        bom_items.append({
            "Component": name,
            "Qty": 1,
            "Category": category,
            "Vendor": vendor,
            "Price": f"INR {cost_inr}",
            "Price_Val": cost_inr,
            "Stock": "In Stock",
            "Alternatives": alt_names
        })
        
    total_cost_inr = cost_summary.get("total_cost_inr", 0)
    subtotals_inr = cost_summary.get("subtotals_inr", {})
    
    # --- Generate CSV ---
    csv_filename = f"{file_id}_bom.csv"
    csv_filepath = os.path.join(EXPORT_DIR, csv_filename)
    with open(csv_filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Component", "Qty", "Category", "Vendor", "Price", "Stock", "Alternatives"])
        for item in bom_items:
            writer.writerow([
                item["Component"], item["Qty"], item["Category"], 
                item["Vendor"], item["Price"], item["Stock"], item["Alternatives"]
            ])
        writer.writerow([])
        writer.writerow(["Total Build Cost", "", "", "", f"INR {total_cost_inr}", "", ""])

    # --- Generate JSON ---
    json_filename = f"{file_id}_bom.json"
    json_filepath = os.path.join(EXPORT_DIR, json_filename)
    json_payload = {
        "bom_items": bom_items,
        "cost_summary": {
            "total_estimated_cost": f"INR {total_cost_inr}",
            "subtotals": {cat: f"INR {val}" for cat, val in subtotals_inr.items()}
        }
    }
    with open(json_filepath, mode='w', encoding='utf-8') as f:
        json.dump(json_payload, f, indent=2)

    # --- Generate Markdown ---
    md_filename = f"{file_id}_bom.md"
    md_filepath = os.path.join(EXPORT_DIR, md_filename)
    with open(md_filepath, mode='w', encoding='utf-8') as f:
        f.write(f"# Bill of Materials (BOM) - Exported Package\n\n")
        f.write(f"| Component | Qty | Category | Vendor | Price | Stock | Alternatives |\n")
        f.write(f"| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for item in bom_items:
            f.write(f"| {item['Component']} | {item['Qty']} | {item['Category']} | {item['Vendor']} | {item['Price']} | {item['Stock']} | {item['Alternatives']} |\n")
            
        f.write(f"\n## Financial Summary\n\n")
        for cat, val in subtotals_inr.items():
            f.write(f"* **{cat}**: INR {val}\n")
        f.write(f"\n**Total Estimated Build Cost: INR {total_cost_inr}**\n")

    return {
        "csv": f"/api/exports/{csv_filename}",
        "json": f"/api/exports/{json_filename}",
        "markdown": f"/api/exports/{md_filename}"
    }
