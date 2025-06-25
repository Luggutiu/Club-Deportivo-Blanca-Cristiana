from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SeccionInformativa
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path

import os
from pathlib import Path

# Configura el directorio de plantillas de forma absoluta
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

router = APIRouter()

@router.get("/mision", response_class=HTMLResponse)
async def mision(request: Request, db: Session = Depends(get_db)):
    contenido = db.query(SeccionInformativa).filter_by(titulo="mision").first()
    return templates.TemplateResponse("ver_seccion.html", {
        "request": request,
        "titulo": "Misión",
        "contenido": contenido.contenido if contenido else "Contenido no disponible"
    })

@router.get("/vision", response_class=HTMLResponse)
async def vision(request: Request):
    return templates.TemplateResponse("vision.html", {"request": request})

@router.get("/quienes-somos", response_class=HTMLResponse)
async def quienes_somos(request: Request):
    return templates.TemplateResponse("quienes_somos.html", {"request": request})

@router.get("/contacto", response_class=HTMLResponse)
async def contacto(request: Request):
    return templates.TemplateResponse("contacto.html", {"request": request})