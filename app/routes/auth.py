from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ⚠️ Toma credenciales solo de variables de entorno

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")

@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if username.strip().lower() == ADMIN_USER.lower() and password.strip() == ADMIN_PASS:
        request.session["admin_logged"] = True
        return RedirectResponse(url="/admin", status_code=HTTP_302_FOUND)

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Usuario o contraseña incorrectos"
    })

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=HTTP_302_FOUND)

def check_admin_logged(request: Request) -> bool:
    return request.session.get("admin_logged", False)