from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import routers
from routes import auth, items, inspection, tms

app = FastAPI(title="UDM Portal Clone")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount reports directory for PDFs
app.mount("/reports", StaticFiles(directory="data/reports"), name="reports")

# Templates directory
templates = Jinja2Templates(directory="templates")

# API routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(items.router, prefix="/items", tags=["items"])
app.include_router(inspection.router, prefix="/inspection", tags=["inspection"])
app.include_router(tms.router, prefix="/tms", tags=["tms"])  # ✅ Added TMS routes
app.include_router(tms.router, prefix="/tms", tags=["tms"])
app.include_router(tms.router, prefix="/tms", tags=["tms"])

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
