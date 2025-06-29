from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SeccionInformativa

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

SECCIONES = {
    "mision": "Misión",
    "vision": "Visión",
    "quienes-somos": "¿Quiénes Somos?",
    "contacto": "Contáctenos"
}

@router.get("/info/{seccion_slug}", response_class=HTMLResponse)
async def ver_seccion(request: Request, seccion_slug: str, db: Session = Depends(get_db)):
    # 🚫 Excluir rutas importantes que no deben tratarse como secciones
    if seccion_slug in ["suscribirse", "auth", "login", "static"]:
        return RedirectResponse(url=f"/{seccion_slug}")

    seccion = db.query(SeccionInformativa).filter_by(slug=seccion_slug).first()

    if not seccion:
        return templates.TemplateResponse("ver_seccion.html", {
            "request": request,
            "titulo": "Sección no encontrada",
            "contenido": "La sección solicitada no está disponible.",
            "imagen_url": None
        })

    return templates.TemplateResponse("ver_seccion.html", {
        "request": request,
        "titulo": seccion.titulo,
        "contenido": seccion.contenido,
        "imagen_url": seccion.imagen_url
    })