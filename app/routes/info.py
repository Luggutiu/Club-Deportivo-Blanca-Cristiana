from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.models import SeccionInformativa

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ✅ Lista de rutas que no deben ser capturadas por /{slug}
RUTAS_EXCLUIDAS = {
    "suscribirse", "contacto", "admin", "login", "logout",
    "static", "favicon.ico", "formulario-suscriptor", "guardar-suscriptor"
}

@router.get("/{slug}", response_class=HTMLResponse)
async def ver_seccion_individual(
    request: Request,
    slug: str,
    db: Session = Depends(get_db)
):
    if slug in RUTAS_EXCLUIDAS:
        raise HTTPException(status_code=404, detail="Ruta no válida")

    seccion = db.query(SeccionInformativa).filter_by(slug=slug).first()

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