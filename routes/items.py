from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from datetime import date
import json
from utils.qr_utils import generate_qr_base64

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ------------------ File paths ------------------
ITEMS_FILE = Path("items.json")
REPAIRS_FILE = Path("repairs.json")
MAINTENANCE_FILE = Path("maintenance.json")

# ------------------ Helpers ------------------
def load_json(path: Path, default):
    if path.exists() and path.stat().st_size > 0:
        try:
            with open(path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return default
    return default

def save_json(path: Path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# ------------------ Load Data ------------------
ITEMS = load_json(ITEMS_FILE, [])
REPAIRS = load_json(REPAIRS_FILE, {})
MAINTENANCE = load_json(MAINTENANCE_FILE, {})

# ✅ Ensure every item has a qr_code
changed = False
for item in ITEMS:
    if "qr_code" not in item or not item["qr_code"]:
        item["qr_code"] = generate_qr_base64(item["rid"])
        changed = True
if changed:
    save_json(ITEMS_FILE, ITEMS)

# ------------------ Routes ------------------

@router.get("/", tags=["items"])
def get_items():
    return ITEMS

@router.get("/view", response_class=HTMLResponse)
def view_items(request: Request):
    return templates.TemplateResponse("items.html", {"request": request, "items": ITEMS})

@router.get("/add", response_class=HTMLResponse)
def add_item_form(request: Request):
    return templates.TemplateResponse("add_item.html", {"request": request})

@router.post("/add", response_class=HTMLResponse)
def add_item(
    request: Request,
    rid: str = Form(...),
    type: str = Form(...),
    manufacturer: str = Form(...),
    batch: str = Form(...),
    material: str = Form(...),
    installed: str = Form(...),
    status: str = Form(...),
    location: str = Form(...),
):
    new_item = {
        "rid": rid,
        "type": type,
        "manufacturer": manufacturer,
        "batch": batch,
        "material": material,
        "installed": installed,
        "status": status,
        "location": location,
        "qr_code": generate_qr_base64(rid)  # ✅ stored at creation
    }
    ITEMS.append(new_item)
    save_json(ITEMS_FILE, ITEMS)
    return RedirectResponse(url="/items/view", status_code=303)

# ------------------ Repairs & Maintenance ------------------

@router.get("/{rid}/repairs")
def get_repairs(rid: str):
    return REPAIRS.get(rid, [])

@router.get("/{rid}/maintenance")
def get_maintenance(rid: str):
    return MAINTENANCE.get(rid, [])

# ------------------ Get single item ------------------
@router.get("/{rid}", tags=["items"])
def get_item(rid: str):
    for item in ITEMS:
        if item["rid"] == rid:
            return item
    return {"error": "Item not found"}
