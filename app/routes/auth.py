from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ⚠️ Para producción, NO dejes las credenciales hardcodeadas
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

@router.get("/login")
async def login_form(request: Request):
    # Renderiza formulario de login sin errores
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    print(f"🔐 Intento login - username: '{username}' | password: '{password}'")
    print(f"Comparando con: '{ADMIN_USER}' y '{ADMIN_PASS}'")

    if username.strip() == ADMIN_USER and password.strip() == ADMIN_PASS:
        request.session["admin_logged"] = True
        print("✅ Login exitoso")
        return RedirectResponse(url="/admin", status_code=HTTP_302_FOUND)

    print("❌ Login fallido")
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Usuario o contraseña incorrectos"
    })

@router.get("/logout")
async def logout(request: Request):
    # Limpia la sesión y redirige al inicio
    request.session.clear()
    return RedirectResponse(url="/", status_code=HTTP_302_FOUND)

# Función reutilizable para verificar si el admin está autenticado
def check_admin_logged(request: Request) -> bool:
    return request.session.get("admin_logged", False)