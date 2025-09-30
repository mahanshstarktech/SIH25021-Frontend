# routes/inspection.py
import os
from fastapi import APIRouter, UploadFile, Form, File, Body
from fastapi.responses import JSONResponse
from src.report_generator import generate_report, generate_pdf

router = APIRouter()

PHOTO_DIR = "data/photos"
os.makedirs(PHOTO_DIR, exist_ok=True)

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
    """
    Submit inspection form:
    - Saves the uploaded photo to 'data/photos/'
    - Generates the JSON report
    """
    photo_filename = None
    if photo:
        photo_filename = photo.filename
        file_path = os.path.join(PHOTO_DIR, photo_filename)
        with open(file_path, "wb") as f:
            f.write(await photo.read())

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
        "photo_filename": photo_filename,
    }

    report = generate_report(form_data)
    return JSONResponse(content={"status": "success", "report": report})


@router.post("/generate_pdf")
async def generate_pdf_endpoint(report: dict = Body(...)):
    """
    Generates PDF from report JSON.
    Embeds the uploaded photo if it exists.
    """
    pdf_file = generate_pdf(report)
    pdf_url = f"/reports/{os.path.basename(pdf_file)}"
    return {"status": "success", "pdf_file": pdf_file, "pdf_url": pdf_url}
