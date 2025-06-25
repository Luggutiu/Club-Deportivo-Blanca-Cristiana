from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.database import SessionLocal
from app import models

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    db = SessionLocal()
    posts = db.query(models.Post).all()
    db.close()
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})

from fastapi import Form, status
from fastapi.responses import RedirectResponse

@router.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "admin":
        response = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="user", value=username)
        return response
    else:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Usuario o contraseña incorrectos"
            }
        )