from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SeccionInformativa
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

router = APIRouter()

@router.get("/admin/secciones/{seccion}", response_class=HTMLResponse)
def editar_seccion(seccion: str, request: Request, db: Session = Depends(get_db)):
    contenido = db.query(SeccionInformativa).filter_by(titulo=seccion).first()
    return templates.TemplateResponse("editar_seccion.html", {
        "request": request,
        "seccion": seccion,
        "contenido": contenido
    })

@router.post("/admin/secciones/{seccion}")
def guardar_seccion(
    seccion: str,
    contenido: str = Form(...),
    db: Session = Depends(get_db)
):
    seccion_bd = db.query(SeccionInformativa).filter_by(titulo=seccion).first()
    if not seccion_bd:
        seccion_bd = SeccionInformativa(titulo=seccion, contenido=contenido)
        db.add(seccion_bd)
    else:
        seccion_bd.contenido = contenido
    db.commit()
    return RedirectResponse(url=f"/{seccion}", status_code=303)