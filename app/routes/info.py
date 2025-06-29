from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.models import SeccionInformativa
from app.database import get_db
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Coloca un prefijo para evitar conflicto con rutas reales
@router.get("/seccion/{seccion_slug}", response_class=HTMLResponse)
def mostrar_seccion(seccion_slug: str, request: Request, db: Session = Depends(get_db)):
    seccion = db.query(SeccionInformativa).filter_by(titulo=seccion_slug).first()
    if seccion:
        return templates.TemplateResponse("seccion.html", {
            "request": request,
            "contenido": seccion,
            "titulo": seccion_slug
        })
    return HTMLResponse("Sección no encontrada", status_code=404)