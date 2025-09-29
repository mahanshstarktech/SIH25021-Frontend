from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import os
from src.report_generator import generate_report, generate_pdf

router = APIRouter()

# Input validation model
class InspectionForm(BaseModel):
    damage_type: str
    severity: str
    action_required: str
    photo_filename: Optional[str] = None
    inspector_name: str
    inspector_id: str
    vendor: Optional[str] = None
    batch: Optional[str] = None
    location: Optional[str] = None
    timestamp: Optional[str] = None

@router.post("/generate_report")
async def generate_report_endpoint(form: InspectionForm):
    form_data = form.dict()
    report = generate_report(form_data)
    return {"status": "success", "report": report}

@router.post("/generate_report_pdf")
async def generate_report_pdf_endpoint(form: InspectionForm):
    form_data = form.dict()
    report = generate_report(form_data)
    pdf_file = generate_pdf(report)
    pdf_url = f"/reports/{os.path.basename(pdf_file)}"
    return {
        "status": "success",
        "report_id": report["report_id"],
        "pdf_file": pdf_file,
        "pdf_url": pdf_url
    }
