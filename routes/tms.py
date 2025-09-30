import json
from datetime import datetime
from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

TMS_FILE = "data/tms_entries.json"

# Ensure file exists
if not os.path.exists(TMS_FILE):
    with open(TMS_FILE, "w") as f:
        json.dump([], f)

def load_entries():
    with open(TMS_FILE, "r") as f:
        return json.load(f)

def save_entries(entries):
    with open(TMS_FILE, "w") as f:
        json.dump(entries, f, indent=4)

@router.post("/post", response_class=JSONResponse)
async def post_to_tms(report_id: str = Form(...), filename: str = Form(...)):
    entries = load_entries()
    new_entry = {
        "report_id": report_id,
        "filename": filename,
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    entries.append(new_entry)
    save_entries(entries)
    return {"status": "success", "message": "Report posted to TMS"}

@router.get("/portal", response_class=HTMLResponse)
async def view_tms_portal(request: Request):
    entries = load_entries()
    return templates.TemplateResponse("tms.html", {"request": request, "entries": entries})


@router.post("/upload")
async def upload_to_tms(request: Request):
    body = await request.json()

    pdf_url = body.get("pdf_url", "")
    filename = os.path.basename(pdf_url) if pdf_url else None

    entry = {
        "report_id": body.get("report_id"),
        "pdf_url": pdf_url,               # e.g. /reports/RPT-2025-09-29-B2CC05.pdf
        "filename": filename,             # e.g. RPT-2025-09-29-B2CC05.pdf
        "timestamp": body.get("timestamp", datetime.now().isoformat())
    }

    os.makedirs("data", exist_ok=True)
    if os.path.exists(TMS_FILE):
        with open(TMS_FILE, "r") as f:
            entries = json.load(f)
    else:
        entries = []

    entries.append(entry)

    with open(TMS_FILE, "w") as f:
        json.dump(entries, f, indent=4)

    return {"status": "success", "entry": entry}


@router.get("/entries")
async def get_entries():
    if os.path.exists(TMS_FILE):
        with open(TMS_FILE, "r") as f:
            entries = json.load(f)
    else:
        entries = []
    return JSONResponse(content=entries)