from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Credenciales estáticas
ADMIN_USER = "admin"
ADMIN_PASS = "admin123*"

# Verifica si el admin ha iniciado sesión
def check_admin_logged(request: Request) -> bool:
    return request.session.get("admin_logged") is True

# Muestra formulario de login
@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": None
    })

# Procesa login
@router.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    print("Intento de login:", username, password)  # Debug opcional

    if username.strip() == ADMIN_USER and password.strip() == ADMIN_PASS:
        request.session["admin_logged"] = True
        return RedirectResponse(url="/admin", status_code=HTTP_302_FOUND)

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Usuario o contraseña incorrectos"
    })

# Cierra sesión
@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=HTTP_302_FOUND)