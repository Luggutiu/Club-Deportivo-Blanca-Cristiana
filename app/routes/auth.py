from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and password == ADMIN_PASS:
        response = RedirectResponse(url="/admin", status_code=HTTP_302_FOUND)
        response.set_cookie("admin_logged", "true")
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Usuario o contraseña incorrectos"})

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=HTTP_302_FOUND)
    response.delete_cookie("admin_logged")
    return response

from fastapi import Request

def check_admin_logged(request: Request):
    return request.session.get("admin_logged", False)