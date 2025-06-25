from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SeccionInformativa
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/mision", response_class=HTMLResponse)
async def mision(request: Request, db: Session = Depends(get_db)):
    contenido = db.query(SeccionInformativa).filter_by(titulo="mision").first()
    return templates.TemplateResponse("ver_seccion.html", {
        "request": request,
        "titulo": "Misión",
        "contenido": contenido.contenido if contenido else "Contenido no disponible"
    })

@router.get("/vision", response_class=HTMLResponse)
async def vision(request: Request, db: Session = Depends(get_db)):
    contenido = db.query(SeccionInformativa).filter_by(titulo="vision").first()
    return templates.TemplateResponse("ver_seccion.html", {
        "request": request,
        "titulo": "Visión",
        "contenido": contenido.contenido if contenido else "Contenido no disponible"
    })

@router.get("/quienes-somos", response_class=HTMLResponse)
async def quienes_somos(request: Request, db: Session = Depends(get_db)):
    contenido = db.query(SeccionInformativa).filter_by(titulo="quienes somos").first()
    return templates.TemplateResponse("ver_seccion.html", {
        "request": request,
        "titulo": "¿Quiénes Somos?",
        "contenido": contenido.contenido if contenido else "Contenido no disponible"
    })

@router.get("/contacto", response_class=HTMLResponse)
async def contacto(request: Request, db: Session = Depends(get_db)):
    contenido = db.query(SeccionInformativa).filter_by(titulo="contacto").first()
    return templates.TemplateResponse("ver_seccion.html", {
        "request": request,
        "titulo": "Contáctenos",
        "contenido": contenido.contenido if contenido else "Contenido no disponible"
    })
