from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import date
from pathlib import Path
import json
from utils.qr_utils import generate_qr_base64

router = APIRouter()
templates = Jinja2Templates(directory="templates")

DATA_FILE = Path("items.json")

def load_items():
    if DATA_FILE.exists() and DATA_FILE.stat().st_size > 0:
        try:
            with open(DATA_FILE, "r") as f:
                items = json.load(f)

            # ✅ Migration: ensure each item has a qr_code
            changed = False
            for item in items:
                if "qr_code" not in item or not item["qr_code"]:
                    item["qr_code"] = generate_qr_base64(item["rid"])
                    changed = True

            if changed:
                with open(DATA_FILE, "w") as f:
                    json.dump(items, f, indent=4)

            return items
        except json.JSONDecodeError:
            return []
    return []

def save_items():
    with open(DATA_FILE, "w") as f:
        json.dump(ITEMS, f, indent=4)

# Load initial items with migration
ITEMS = load_items()

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
    save_items()
    return RedirectResponse(url="/items/view", status_code=303)

@router.get("/{rid}", tags=["items"])
def get_item(rid: str):
    for item in ITEMS:
        if item["rid"] == rid:
            return item
    return {"error": "Item not found"}
