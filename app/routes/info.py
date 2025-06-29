from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SeccionInformativa
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# 🧠 Solo acepta ciertos slugs conocidos
SECCIONES_VALIDAS = {
    "mision": "Misión",
    "vision": "Visión",
    "quienes-somos": "¿Quiénes somos?"
}

@router.get("/{seccion_slug}", response_class=HTMLResponse)
async def ver_seccion(request: Request, seccion_slug: str, db: Session = Depends(get_db)):
    # 🔒 Validar solo slugs definidos
    if seccion_slug not in SECCIONES_VALIDAS:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": "Sección no encontrada"
        }, status_code=404)

    titulo = SECCIONES_VALIDAS[seccion_slug]
    seccion = db.query(SeccionInformativa).filter_by(titulo=titulo).first()

    if not seccion:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": "Contenido no disponible para esta sección"
        }, status_code=404)

    return templates.TemplateResponse("ver_seccion.html", {
        "request": request,
        "titulo": seccion.titulo,
        "contenido": seccion.contenido,
        "imagen_url": seccion.imagen_url
    })