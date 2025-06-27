from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.models import Post, SeccionInformativa, Horario
from app.routes.auth import check_admin_logged
from app.routes.embedder import generar_embed

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# -----------------------------------------
# Panel principal admin
# -----------------------------------------
@router.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request, db: Session = Depends(get_db)):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)

    publicaciones = db.query(Post).order_by(Post.id.desc()).all()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "publicaciones": publicaciones
    })


# -----------------------------------------
# Publicar un post (texto, imagen y video)
# -----------------------------------------
@router.post("/admin/publicar-post")
def publicar_post(
    request: Request,
    titulo: str = Form(...),
    contenido_texto: str = Form(...),
    imagen_url: str = Form(None),
    url: str = Form(None),
    plataforma: str = Form(None),
    db: Session = Depends(get_db)
):
    embed_url = ""
    if url and plataforma:
        embed_url = generar_embed(url, plataforma)

    nuevo_post = Post(
        titulo=titulo,
        contenido_texto=contenido_texto,
        imagen_url=imagen_url,
        url=url,
        embed_url=embed_url,
        plataforma=plataforma
    )
    db.add(nuevo_post)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)


# -----------------------------------------
# Editar secciones informativas
# -----------------------------------------
@router.get("/admin/editar/{seccion}", response_class=HTMLResponse)
def editar_seccion(request: Request, seccion: str, db: Session = Depends(get_db)):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)

    contenido = db.query(SeccionInformativa).filter_by(titulo=seccion).first()
    if not contenido:
        contenido = SeccionInformativa(titulo=seccion, contenido="")

    return templates.TemplateResponse("editar_seccion.html", {
        "request": request,
        "seccion": seccion,
        "contenido": contenido
    })

@router.post("/admin/editar/{seccion}")
def guardar_seccion(
    request: Request,
    seccion: str,
    contenido: str = Form(...),
    db: Session = Depends(get_db)
):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)

    seccion_obj = db.query(SeccionInformativa).filter_by(titulo=seccion).first()

    if not seccion_obj:
        seccion_obj = SeccionInformativa(titulo=seccion, contenido=contenido)
        db.add(seccion_obj)
    else:
        seccion_obj.contenido = contenido

    db.commit()
    return RedirectResponse(url="/admin", status_code=302)


# -----------------------------------------
# Gestionar horarios
# -----------------------------------------
@router.get("/admin/gestionar-horarios", response_class=HTMLResponse)
def gestionar_horarios(request: Request, db: Session = Depends(get_db)):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)

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
    actividad: str = Form(...),
    db: Session = Depends(get_db)
):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)

    nuevo_horario = Horario(
        dia=dia,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        actividad=actividad,
        publicado=False
    )
    db.add(nuevo_horario)
    db.commit()
    return RedirectResponse(url="/admin/gestionar-horarios", status_code=303)