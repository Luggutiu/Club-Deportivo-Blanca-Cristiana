# ========================================
# Proyecto desarrollado exclusivamente para:
# Club Deportivo Blanca Cristiana
# Desarrollador: Luis Gutierrez
# Sitio: https://club-deportivo-blanca-cristiana.onrender.com
# Email: clubdeportivoblancacristiana@gmail.com
# Año: 2025
# Todos los derechos reservados
# ========================================

from fastapi import APIRouter, Request, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.status import HTTP_303_SEE_OTHER

from app.models import Suscriptor, SeccionInformativa, Horario, Post
from app.database import get_db
from app.routes.auth import check_admin_logged
from app.routes.embedder import generar_embed

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
import openpyxl
from io import BytesIO
import os
import shutil




import openpyxl

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ------------------------ SECCIONES ------------------------

@router.get("/admin/editar/{slug}", response_class=HTMLResponse)
def editar_seccion(slug: str, request: Request, db: Session = Depends(get_db)):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login")

    contenido = db.query(SeccionInformativa).filter_by(slug=slug).first()
    if not contenido:
        raise HTTPException(status_code=404, detail="Sección no encontrada")

    return templates.TemplateResponse("editar_seccion.html", {
        "request": request,
        "seccion": contenido.titulo,
        "contenido": contenido,
        "imagen_url": contenido.imagen_url
    })


@router.post("/admin/editar/{slug}")
def guardar_seccion(
    slug: str,
    contenido: str = Form(...),
    imagen_url: str = Form(None),
    db: Session = Depends(get_db),
    request: Request = None
):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=303)

    seccion_bd = db.query(SeccionInformativa).filter_by(slug=slug).first()
    if not seccion_bd:
        raise HTTPException(status_code=404, detail="Sección no encontrada")

    seccion_bd.contenido = contenido
    seccion_bd.imagen_url = imagen_url
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)


# ------------------------ PUBLICAR VIDEO ------------------------

@router.get("/admin/publicar-video", response_class=HTMLResponse)
def publicar_video_form(request: Request):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("publicar_video.html", {"request": request})
from typing import Optional

@router.post("/admin/publicar-video")
async def procesar_video(
    request: Request,
    titulo: Optional[str] = Form(""),
    url: Optional[str] = Form(""),
    plataforma: Optional[str] = Form(""),
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


# ------------------------ PUBLICAR POST ------------------------

from fastapi import APIRouter, Request, Form, UploadFile, File, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os, shutil
from app.database import get_db
from app.models import Post
from app.utils import check_admin_logged
from app.routes.embedder import generar_embed

router = APIRouter()

@router.post("/admin/publicar-post")
async def publicar_post(
    request: Request,
    titulo: str = Form(...),
    texto: str = Form(...),
    imagen_url: str = Form(None),
    db: Session = Depends(get_db)
):
    try:
        nuevo_post = Post(
            titulo=titulo,
            texto=texto,
            imagen_url=imagen_url
        )
        db.add(nuevo_post)
        db.commit()
        db.refresh(nuevo_post)
        return RedirectResponse(url="/admin", status_code=302)
    except Exception as e:
        print("Error al publicar:", e)
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": str(e)
        }, status_code=500)
        




# ============================
# Reporte de Suscriptores - Vista HTML
# ============================

@router.get("/admin/reporte-suscriptores", response_class=HTMLResponse)
async def ver_reporte_suscriptores(
    request: Request,
    db: Session = Depends(get_db),
    admin: bool = Depends(check_admin_logged)
):
    suscriptores = db.query(Suscriptor).all()
    return templates.TemplateResponse("reporte_suscriptores.html", {
        "request": request,
        "suscriptores": suscriptores
    })

# ============================
# Descargar Suscriptores en Excel (.xlsx)
# ============================

@router.get("/admin/descargar-suscriptores")
async def descargar_excel_suscriptores(
    db: Session = Depends(get_db),
    admin: bool = Depends(check_admin_logged)
):
    suscriptores = db.query(Suscriptor).all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Suscriptores"

    # Encabezados
    headers = ["ID", "Nombre", "Correo", "Teléfono", "Fecha de Suscripción"]
    ws.append(headers)

    # Agregar datos
    for s in suscriptores:
        ws.append([
            s.id,
            s.nombre,
            s.correo,
            s.telefono,
            s.fecha.strftime("%Y-%m-%d %H:%M:%S")
        ])

    # Preparar archivo para descarga
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=suscriptores.xlsx"
        }
    )