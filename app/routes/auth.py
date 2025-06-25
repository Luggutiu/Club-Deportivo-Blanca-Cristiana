from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"  # más adelante se cifrará

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and password == ADMIN_PASS:
        response = RedirectResponse(url="/admin", status_code=HTTP_302_FOUND)
        response.set_cookie(key="admin_logged", value="true")
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Credenciales inválidas"})

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=HTTP_302_FOUND)
    response.delete_cookie("admin_logged")
    return response

def check_admin_logged(request: Request):
    return request.cookies.get("admin_logged") == "true"

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    if not check_admin_logged(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

from app import models
from app.database import SessionLocal
import re

def detect_platform(url: str):
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "facebook.com" in url:
        return "facebook"
    elif "instagram.com" in url:
        return "instagram"
    elif "tiktok.com" in url:
        return "tiktok"
    else:
        return "unknown"

@router.post("/create")
async def create_post(request: Request, title: str = Form(...), url: str = Form(...)):
    if not check_admin_logged(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    platform = detect_platform(url)
    db = SessionLocal()
    post = models.Post(title=title, url=url, platform=platform)
    db.add(post)
    db.commit()
    db.close()
    return RedirectResponse(url="/posts", status_code=302)

from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Login GET
@router.get("/login")
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Login POST (básico sin hash, por ahora)
@router.post("/login")
def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    if email == "admin@club.com" and password == "admin123":
        response = RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
        response.set_cookie("authenticated", "yes")  # Cookie simple para validar sesión
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Credenciales incorrectas"})