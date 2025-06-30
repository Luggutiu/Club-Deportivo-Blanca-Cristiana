from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Post

router = APIRouter()

@router.post("/like/{post_id}")
def dar_like(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    post.likes += 1
    db.commit()
    return {"likes": post.likes}


from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/suscribirse")
def suscribirse(request: Request):
    return templates.TemplateResponse("public/suscribirse.html", {"request": request})


# En app/routes/public.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Suscriptor
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/suscribirse", response_class=HTMLResponse)
def formulario_suscripcion(request: Request):
    return templates.TemplateResponse("public/suscribirse.html", {"request": request})

@router.post("/suscribirse")
def registrar_suscriptor(
    request: Request,
    nombre: str = Form(...),
    correo: str = Form(...),
    db: Session = Depends(get_db)
):
    nuevo = Suscriptor(nombre=nombre, correo=correo)
    db.add(nuevo)
    db.commit()
    return RedirectResponse(url="/", status_code=302)

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/politica-privacidad", response_class=HTMLResponse)
async def politica_privacidad(request: Request):
    return templates.TemplateResponse("politica_privacidad.html", {"request": request})