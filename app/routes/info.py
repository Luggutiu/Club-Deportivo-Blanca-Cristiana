from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SeccionInformativa
from fastapi import HTTPException

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

SECCIONES = {
    "mision": "Misión",
    "vision": "Visión",
    "quienes-somos": "¿Quiénes Somos?",
    "contacto": "Contáctenos"
}


templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

@router.get("/{seccion_slug}", response_class=HTMLResponse)
async def ver_seccion(request: Request, seccion_slug: str, db: Session = Depends(get_db)):
    # Excluir rutas reservadas
    if seccion_slug in ["admin", "login", "logout", "static", "suscribirse", "auth", "guardar-suscriptor", "formulario-suscriptor"]:
        raise HTTPException(status_code=404)

    seccion = db.query(SeccionInformativa).filter_by(slug=seccion_slug).first()
    if not seccion:
        raise HTTPException(status_code=404)

    return templates.TemplateResponse("ver_seccion.html", {
        "request": request,
        "titulo": seccion.titulo,
        "contenido": seccion.contenido,
        "imagen_url": seccion.imagen_url
    })