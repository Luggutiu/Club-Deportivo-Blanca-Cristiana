from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SeccionInformativa, Horario
from app.routes.auth import check_admin_logged

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ------------------------ SECCIONES ------------------------

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
def guardar_seccion(
    seccion: str,
    contenido: str = Form(...),
    db: Session = Depends(get_db),
    request: Request = None
):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=303)

    seccion_bd = db.query(SeccionInformativa).filter_by(titulo=seccion).first()
    if not seccion_bd:
        seccion_bd = SeccionInformativa(titulo=seccion, contenido=contenido)
        db.add(seccion_bd)
    else:
        seccion_bd.contenido = contenido

    db.commit()

    # Redirección corregida:
    return RedirectResponse(url="/admin", status_code=303)

# ------------------------ PUBLICAR VIDEO ------------------------

@router.get("/admin/publicar-video", response_class=HTMLResponse)
def publicar_video_form(request: Request):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("publicar_video.html", {"request": request})

# ------------------------ GESTIONAR HORARIOS ------------------------

@router.get("/admin/gestionar-horarios", response_class=HTMLResponse)
def gestionar_horarios(request: Request, db: Session = Depends(get_db)):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login")
    
    horarios = db.query(Horario).order_by(Horario.dia).all()
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
    actividad: str = Form(...),
    db: Session = Depends(get_db)
):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login")
    
    nuevo_horario = Horario(
        dia=dia,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        actividad=actividad
    )
    db.add(nuevo_horario)
    db.commit()
    return RedirectResponse(url="/admin/gestionar-horarios", status_code=303)