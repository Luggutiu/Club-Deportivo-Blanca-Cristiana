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


@router.post("/admin/publicar-video")
async def procesar_video(
    request: Request,
    titulo: str = Form(...),
    url: str = Form(...),
    plataforma: str = Form(...),
    db: Session = Depends(get_db)
):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)

    embed_url = generar_embed(url, plataforma)

    nuevo_post = Post(
        titulo=titulo,
        url=url,
        plataforma=plataforma,
        embed_url=embed_url
    )
    db.add(nuevo_post)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

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

from fastapi import APIRouter, Request, Form, UploadFile, File, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os, shutil

from app.database import get_db
from app.models import Post
from app.routes.auth import check_admin_logged
from app.routes.embedder import generar_embed

router = APIRouter()


@router.post("/admin/publicar-post")
async def publicar_post(
    request: Request,
    titulo: str = Form(...),
    texto: str = Form(None),
    imagen_url: str = Form(None),
    imagen_archivo: UploadFile = File(None),
    url: str = Form(None),
    plataforma: str = Form(None),
    db: Session = Depends(get_db)
):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)

    embed_url = ""
    if url and plataforma:
        embed_url = generar_embed(url, plataforma)

    filename = None
    if imagen_archivo:
        uploads_dir = "app/static/uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        filename = imagen_archivo.filename
        path = os.path.join(uploads_dir, filename)
        with open(path, "wb") as buffer:
            shutil.copyfileobj(imagen_archivo.file, buffer)

    nuevo_post = Post(
        titulo=titulo,
        texto=texto,
        imagen_url=imagen_url,
        imagen_archivo=filename,
        url=url,
        embed_url=embed_url,
        plataforma=plataforma
    )
    db.add(nuevo_post)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from app.dependencies import get_db
from app.models import Horario  # Asegúrate de que la ruta sea correcta

router = APIRouter()

from fastapi import Request

@router.post("/admin/publicar-horario/{horario_id}")
def publicar_horario(
    request: Request,
    horario_id: int,
    db: Session = Depends(get_db)
):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)

    horario = db.query(Horario).filter(Horario.id == horario_id).first()
    if horario:
        horario.publicado = True
        db.commit()
    return RedirectResponse(url="/admin/gestionar-horarios", status_code=303)