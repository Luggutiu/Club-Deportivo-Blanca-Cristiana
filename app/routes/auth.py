import os
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
from starlette.middleware.sessions import SessionMiddleware

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ⚠️ Toma credenciales solo de variables de entorno
ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASS = os.getenv("ADMIN_PASS")

def check_admin_logged(request: Request) -> bool:
    return bool(request.session.get("admin_logged"))

@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    # Limpia espacios
    user = username.strip()
    pwd  = password.strip()

    if user == ADMIN_USER and pwd == ADMIN_PASS:
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