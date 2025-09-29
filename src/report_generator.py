import datetime
import uuid
import os
from .rules import get_condition_score, get_predicted_failure_risk, get_suggested_sku, check_vendor_alert
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

REPORTS_DIR = "data/reports"

def generate_report(form_data: dict) -> dict:
    report_id = f"RPT-{datetime.date.today().isoformat()}-{uuid.uuid4().hex[:6].upper()}"

    severity = form_data.get("severity", "Medium")
    damage_type = form_data.get("damage_type", "Loose")
    vendor = form_data.get("vendor")
    batch = form_data.get("batch")

    condition_score = get_condition_score(severity)
    predicted_failure_risk = get_predicted_failure_risk(severity)
    suggested_sku = get_suggested_sku(damage_type)
    vendor_alert = check_vendor_alert(vendor, batch) if vendor and batch else None

    work_order = {
        "priority_level": severity,
        "action": form_data.get("action_required", "Monitor"),
        "spare_part_sku": suggested_sku,
        "assigned_to": "Jaipur Maintenance Division",
        "status": "Pending"
    }

    report = {
        "report_id": report_id,
        "inspected_item": form_data,
        "ai_analysis": {
            "condition_score": condition_score,
            "predicted_failure_risk": predicted_failure_risk,
            "vendor_score": vendor_alert or "No vendor alert"
        },
        "work_order": work_order,
        "approval": {
            "supervisor_signature": "",
            "date": None
        }
    }

    return report

def generate_pdf(report: dict) -> str:
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

    report_id = report.get("report_id", "RPT-UNKNOWN")
    filename = f"{REPORTS_DIR}/{report_id}.pdf"

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, f"Inspection Report: {report_id}")
    y -= 40

    c.setFont("Helvetica", 12)
    # Inspected Item
    c.drawString(50, y, "Inspected Item:")
    y -= 20
    for key, value in report.get("inspected_item", {}).items():
        c.drawString(70, y, f"{key}: {value}")
        y -= 15

    y -= 10
    # AI Analysis
    c.drawString(50, y, "AI Analysis:")
    y -= 20
    for key, value in report.get("ai_analysis", {}).items():
        c.drawString(70, y, f"{key}: {value}")
        y -= 15

    y -= 10
    # Work Order
    c.drawString(50, y, "Work Order:")
    y -= 20
    for key, value in report.get("work_order", {}).items():
        c.drawString(70, y, f"{key}: {value}")
        y -= 15

    y -= 10
    # Supervisor Approval
    c.drawString(50, y, "Supervisor Approval:")
    y -= 20
    c.drawString(70, y, "Supervisor Signature: ____________________")
    y -= 20
    c.drawString(70, y, f"Date: {datetime.date.today().isoformat()}")
    y -= 20

    c.showPage()
    c.save()
    return filename
