from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app import models
from app.models import SeccionInformativa
from pathlib import Path
import os

# Templates
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

router = APIRouter()

# Seguridad: Validar sesión de admin
def check_admin_logged(request: Request):
    return request.cookies.get("admin_logged") == "true"

# --- Secciones informativas ---

@router.get("/admin/editar/{seccion}", response_class=HTMLResponse)
def editar_seccion(seccion: str, request: Request, db: Session = Depends(get_db)):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login")
    
    contenido = db.query(SeccionInformativa).filter_by(titulo=seccion).first()
    if not contenido:
        raise HTTPException(status_code=404, detail="Sección no encontrada")

    return templates.TemplateResponse("editar_seccion.html", {
        "request": request,
        "seccion": seccion,
        "contenido": contenido
    })

@router.post("/admin/editar/{seccion}")
def guardar_seccion(seccion: str, contenido: str = Form(...), db: Session = Depends(get_db), request: Request = None):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login")

    seccion_bd = db.query(SeccionInformativa).filter_by(titulo=seccion).first()
    if not seccion_bd:
        seccion_bd = SeccionInformativa(titulo=seccion, contenido=contenido)
        db.add(seccion_bd)
    else:
        seccion_bd.contenido = contenido
    db.commit()

    return RedirectResponse(url=f"/{seccion}", status_code=303)

# --- Publicar video ---

@router.get("/admin/publicar-video", response_class=HTMLResponse)
def publicar_video_form(request: Request):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("publicar_video.html", {"request": request})

# --- Gestionar horarios ---

@router.get("/admin/horarios", response_class=HTMLResponse)
def ver_horarios(request: Request):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login")
    
    db = SessionLocal()
    horarios = db.query(models.Horario).all()
    db.close()

    return templates.TemplateResponse("gestionar_horarios.html", {
        "request": request,
        "horarios": horarios
    })
    

    from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Horario
from app.routes.auth import check_admin_logged  # Asegúrate que esta ruta es correcta

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/admin/gestionar-horarios")
def gestionar_horarios(request: Request):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)

    db: Session = SessionLocal()
    horarios = db.query(Horario).all()
    return templates.TemplateResponse("gestionar_horarios.html", {
        "request": request,
        "horarios": horarios
    })


@router.post("/admin/guardar-horario")
def guardar_horario(
    request: Request,
    dia: str = Form(...),
    hora_inicio: str = Form(...),
    hora_fin: str = Form(...),
    actividad: str = Form(...)
):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)

    db: Session = SessionLocal()
    nuevo_horario = Horario(
        dia=dia,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        actividad=actividad,
        publicado=True  # Se publica por defecto
    )
    db.add(nuevo_horario)
    db.commit()
    return RedirectResponse(url="/admin/gestionar-horarios", status_code=302)