# routes/inspection.py
from fastapi import APIRouter, UploadFile, Form, File
from fastapi.responses import JSONResponse
from src.report_generator import generate_report, generate_pdf
from fastapi import Body

router = APIRouter()

@router.post("/submit")
async def submit_inspection(
    damage_type: str = Form(...),
    severity: str = Form(...),
    action_required: str = Form(...),
    inspector_name: str = Form(...),
    inspector_id: str = Form(...),
    vendor: str = Form(None),
    batch: str = Form(None),
    location: str = Form(None),
    rid: str = Form(...),
    timestamp: str = Form(...),
    photo: UploadFile = File(None)
):
    # Build form data
    form_data = {
        "damage_type": damage_type,
        "severity": severity,
        "action_required": action_required,
        "inspector_name": inspector_name,
        "inspector_id": inspector_id,
        "vendor": vendor,
        "batch": batch,
        "location": location,
        "rid": rid,
        "timestamp": timestamp,
        "photo_filename": photo.filename if photo else None,
    }

    report = generate_report(form_data)  # generate JSON report
    return JSONResponse(content={"status": "success", "report": report})


@router.post("/generate_pdf")
async def generate_pdf_endpoint(report: dict = Body(...)):
    pdf_file = generate_pdf(report)
    pdf_url = f"/reports/{pdf_file.split('/')[-1]}"
    return {"status": "success", "pdf_file": pdf_file, "pdf_url": pdf_url}
