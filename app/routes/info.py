from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
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

@router.get("/{seccion_slug}", response_class=HTMLResponse)
async def ver_seccion(request: Request, seccion_slug: str, db: Session = Depends(get_db)):
    if seccion_slug not in SECCIONES:
        return templates.TemplateResponse("ver_seccion.html", {
            "request": request,
            "titulo": "Sección no encontrada",
            "contenido": "La sección solicitada no está disponible.",
            "imagen_url": None
        })

    contenido = db.query(SeccionInformativa).filter_by(titulo=SECCIONES[seccion_slug]).first()
    return templates.TemplateResponse("ver_seccion.html", {
        "request": request,
        "titulo": SECCIONES[seccion_slug],
        "contenido": contenido.contenido if contenido else "",
        "imagen_url": contenido.imagen_url if contenido and contenido.imagen_url else None
    })