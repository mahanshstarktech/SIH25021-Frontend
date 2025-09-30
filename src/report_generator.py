import datetime
import uuid
import os
from .rules import get_condition_score, get_predicted_failure_risk, get_suggested_sku, check_vendor_alert
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


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

    def draw_section(title, data):
        nonlocal y
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, title)
        y -= 25
        c.setFont("Helvetica", 12)

        for key, value in data.items():
            nice_key = key.replace("_", " ").title()

            # Embed the photo if key is photo_filename and file exists
            if key == "photo_filename" and value:
                photo_path = f"data/photos/{value}"  # assuming photos are stored here
                if os.path.exists(photo_path):
                    try:
                        img = ImageReader(photo_path)
                        img_width = 100  # width in points
                        img_height = 100  # height in points
                        c.drawImage(img, 70, y - img_height + 15, width=img_width, height=img_height)
                        y -= img_height + 10
                    except Exception as e:
                        c.drawString(70, y, f"{nice_key}: {value} (Image load failed)")
                        y -= 18
                else:
                    c.drawString(70, y, f"{nice_key}: {value} (Image not found)")
                    y -= 18
            else:
                c.drawString(70, y, f"{nice_key}: {value}")
                y -= 18
        y -= 10  # Extra spacing after section

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, y, f"Inspection Report")
    y -= 40
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y, f"Report ID: {report_id}")
    y -= 40

    # Sections
    draw_section("Inspected Item", report.get("inspected_item", {}))
    draw_section("AI Analysis", report.get("ai_analysis", {}))
    draw_section("Work Order", report.get("work_order", {}))
    draw_section("Supervisor Approval", report.get("approval", {}))

    # Footer
    c.setFont("Helvetica", 12)
    c.drawString(50, 50, f"Generated on: {datetime.date.today().isoformat()}")
    c.showPage()
    c.save()

    return filename