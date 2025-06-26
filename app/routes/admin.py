from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import SessionLocal
from app import models
from app.models import Post, SeccionInformativa, Horario
from app.embedder import generar_embed
from app.routes.admin_info import check_admin_logged  # Asegúrate de tenerlo disponible
from app.utils import detect_platform  # o defínelo aquí si no tienes utils.py

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ---------- Panel principal ----------
@router.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)

    db = SessionLocal()
    publicaciones = db.query(Post).order_by(Post.id.desc()).all()
    db.close()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "publicaciones": publicaciones
    })

# ---------- Publicar video ----------
@router.get("/admin/publicar-video", response_class=HTMLResponse)
def mostrar_form_video(request: Request):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("publicar_video.html", {"request": request})

@router.post("/admin/publicar-video")
def guardar_video(request: Request, title: str = Form(...), url: str = Form(...)):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)

    db = SessionLocal()
    platform = detect_platform(url)
    embed_url, _ = generar_embed(url)
    nuevo = Post(title=title, url=url, platform=platform, embed_url=embed_url)
    db.add(nuevo)
    db.commit()
    db.close()
    return RedirectResponse(url="/posts", status_code=302)

# ---------- Editar secciones ----------
@router.get("/admin/editar/{seccion}", response_class=HTMLResponse)
def editar_seccion(request: Request, seccion: str):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)

    db = SessionLocal()
    contenido = db.query(SeccionInformativa).filter_by(titulo=seccion).first()
    db.close()

    if not contenido:
        contenido = SeccionInformativa(titulo=seccion, contenido="")

    return templates.TemplateResponse("editar_seccion.html", {
        "request": request,
        "seccion": seccion,
        "contenido": contenido
    })

@router.post("/admin/editar/{seccion}")
def guardar_seccion(request: Request, seccion: str, contenido: str = Form(...)):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)

    db = SessionLocal()
    seccion_obj = db.query(SeccionInformativa).filter_by(titulo=seccion).first()

    if not seccion_obj:
        seccion_obj = SeccionInformativa(titulo=seccion, contenido=contenido)
        db.add(seccion_obj)
    else:
        seccion_obj.contenido = contenido

    db.commit()
    db.close()
    return RedirectResponse(url="/admin", status_code=302)

# ---------- Horarios ----------
@router.get("/admin/horarios", response_class=HTMLResponse)
def ver_horarios(request: Request):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)

    db = SessionLocal()
    horarios = db.query(Horario).all()
    db.close()
    return templates.TemplateResponse("gestionar_horarios.html", {"request": request, "horarios": horarios})

@router.post("/admin/horarios")
def agregar_horario(request: Request, dia: str = Form(...), hora: str = Form(...), actividad: str = Form(...)):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)

    db = SessionLocal()
    nuevo = Horario(dia=dia, hora=hora, actividad=actividad)
    db.add(nuevo)
    db.commit()
    db.close()
    return RedirectResponse(url="/admin/horarios", status_code=302)