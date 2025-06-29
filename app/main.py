from fastapi import FastAPI, Request, Depends, Form, UploadFile, File, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_303_SEE_OTHER
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.utils.email_utils import enviar_correo_bienvenida, notificar_admin_suscripcion  # si aún no lo tienes importado
from app.routes.auth import check_admin_logged
import shutil
import os
from app.routes import info


# Modelos y Base de Datos
from app.database import get_db
from app.models import Post, Horario, SeccionInformativa, Suscriptor
from app.routes.embedder import generar_embed
from app.routes.auth import check_admin_logged

# Rutas
from app.routes import like, auth, info, admin_info, admin, posts, dev, auth_google, healthcheck
from app.routes.suscripcion import router as suscripcion_router

# Inicialización
app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Montar rutas
app.include_router(info.router)
app.include_router(like.router)
app.include_router(healthcheck.router)
app.include_router(auth_google.router)
app.include_router(suscripcion_router)
app.include_router(info.router)
app.include_router(admin_info.router)
app.include_router(admin.router)
app.include_router(posts.router)
app.include_router(dev.router)
app.include_router(auth.router)
# --------------------- Rutas Públicas ---------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    try:
        posts = db.query(Post).all()
        horarios = db.query(Horario).filter(Horario.publicado == True).all()
        secciones = {s.titulo: s.contenido for s in db.query(SeccionInformativa).all()}
        publicaciones = posts + horarios
        publicaciones.sort(key=lambda x: getattr(x, 'fecha_creacion', None) or x.id, reverse=True)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "publicaciones": publicaciones,
            "secciones": secciones
        })
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": str(e)
        }, status_code=500)

@app.get("/politica-privacidad", response_class=HTMLResponse)
def politica_privacidad(request: Request):
    return templates.TemplateResponse("politica_privacidad.html", {"request": request})

@app.get("/condiciones-servicio", response_class=HTMLResponse)
def condiciones_servicio(request: Request):
    return templates.TemplateResponse("condiciones_servicio.html", {"request": request})

@app.get("/contacto", response_class=HTMLResponse)
def contacto(request: Request, db=Depends(get_db)):
    seccion = db.query(SeccionInformativa).filter(SeccionInformativa.titulo == "contacto").first()
    return templates.TemplateResponse("contacto.html", {
        "request": request,
        "contenido": seccion
    })

# --------------------- Suscripción clásica ---------------------

@app.get("/suscribirse", response_class=HTMLResponse)
async def mostrar_formulario_suscripcion(
    request: Request,
    success: str = "",
    error: str = "",
    nombre_completo: str = "",
    correo: str = "",
    tipo_documento: str = "",
    numero_documento: str = "",
    celular: str = "",
    acepto: bool = False
):
    return templates.TemplateResponse("suscribirse.html", {
        "request": request,
        "success": success,
        "error": error,
        "nombre_completo": nombre_completo,
        "correo": correo,
        "tipo_documento": tipo_documento,
        "numero_documento": numero_documento,
        "celular": celular,
        "acepto": acepto
    })

@app.post("/suscribirse", response_class=HTMLResponse)
def procesar_suscripcion(
    request: Request,
    nombre: str = Form(...),
    correo: str = Form(...),
    db: Session = Depends(get_db)
):
    nuevo_suscriptor = Suscriptor(nombre=nombre, correo=correo)
    try:
        db.add(nuevo_suscriptor)
        db.commit()
        return templates.TemplateResponse("confirmacion_suscripcion.html", {
            "request": request,
            "nombre": nombre
        })
    except Exception:
        db.rollback()
        return templates.TemplateResponse("suscribirse.html", {
            "request": request,
            "error": "correo_existente",
            "nombre": nombre,
            "correo": correo
        })

@app.post("/guardar-suscriptor", response_class=HTMLResponse)
async def guardar_suscriptor(
    request: Request,
    tipo_documento: str = Form(...),
    numero_documento: str = Form(...),
    nombre_completo: str = Form(...),
    celular: str = Form(...),
    correo: str = Form(...),
    db: Session = Depends(get_db)
):
    

    nuevo = Suscriptor(
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        nombre=nombre_completo,
        nombre_completo=nombre_completo,
        celular=celular,
        correo=correo
    )

    try:
        db.add(nuevo)
        db.commit()

        # Envío de correos
        await enviar_correo_bienvenida(destinatario=correo, nombre=nombre_completo)
        await notificar_admin_suscripcion(
            nombre=nombre_completo,
            correo=correo,
            documento=numero_documento,
            tipo=tipo_documento,
            celular=celular
        )

        return templates.TemplateResponse("confirmacion_suscripcion.html", {
            "request": request,
            "nombre": nombre_completo,
            "correo": correo
        })

    except IntegrityError:
        db.rollback()
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": "Este correo o documento ya está registrado."
        }, status_code=400)

@app.get("/formulario-suscriptor", response_class=HTMLResponse)
def formulario_suscriptor(request: Request, correo: str = Query(None), nombre: str = Query(None)):
    return templates.TemplateResponse("formulario_suscriptor.html", {
        "request": request,
        "correo": correo,
        "nombre": nombre
    })

# --------------------- Panel de Administración ---------------------

@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)
    db = next(get_db())
    publicaciones = db.query(Post).all()
    horarios = db.query(Horario).filter(Horario.publicado == True).all()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "publicaciones": publicaciones,
        "horarios": horarios
    })

@app.get("/admin/publicar-post", response_class=HTMLResponse)
def formulario_publicar_post(request: Request):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("publicar_post.html", {"request": request})

@app.get("/test-embed", response_class=HTMLResponse)
def test_embed(request: Request):
    return templates.TemplateResponse("test_embed.html", {"request": request})

# -------- Gestión de horarios --------
@app.get("/admin/gestionar-horarios", response_class=HTMLResponse)
def mostrar_formulario_horario(request: Request, db=Depends(get_db)):
    horarios = db.query(Horario).order_by(Horario.dia).all()
    return templates.TemplateResponse("gestionar_horarios.html", {
        "request": request,
        "horarios": horarios
    })
    
@app.get("/admin/editar-horario/{horario_id}", response_class=HTMLResponse)
def mostrar_formulario_edicion(request: Request, horario_id: int, db=Depends(get_db)):
    horario = db.query(Horario).filter(Horario.id == horario_id).first()
    if not horario:
        return HTMLResponse("Horario no encontrado", status_code=404)
    return templates.TemplateResponse("editar_horario.html", {
        "request": request,
        "horario": horario
    })
    
@app.post("/admin/guardar-horario")
def guardar_horario(
    request: Request,
    dia: str = Form(...),
    hora_inicio: str = Form(...),
    hora_fin: str = Form(...),
    actividad: str = Form(...),
    db=Depends(get_db)
):
    nuevo_horario = Horario(
        dia=dia,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        actividad=actividad,
        publicado=True
    )
    db.add(nuevo_horario)
    db.commit()
    return RedirectResponse(url="/admin/gestionar-horarios", status_code=303)

@app.post("/admin/publicar-post")
def guardar_post(request: Request, titulo: str = Form(...), texto: str = Form(None), imagen_url: str = Form(None), db=Depends(get_db)):
    nuevo_post = Post(titulo=titulo, texto=texto, imagen_url=imagen_url)
    db.add(nuevo_post)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/eliminar-post/{post_id}")
async def eliminar_post(post_id: int, db=Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    db.delete(post)
    db.commit()
    return RedirectResponse(url="/admin", status_code=HTTP_303_SEE_OTHER)

@app.get("/admin/editar-post/{post_id}", response_class=HTMLResponse)
def mostrar_formulario_editar_post(request: Request, post_id: int, db=Depends(get_db)):
    if not check_admin_logged(request):
        return RedirectResponse(url="/login", status_code=302)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return HTMLResponse("Post no encontrado", status_code=404)
    return templates.TemplateResponse("editar_post.html", {"request": request, "post": post})

@app.post("/admin/editar-post/{post_id}")
def editar_post(request: Request, post_id: int, titulo: str = Form(...), texto: str = Form(None), imagen_url: str = Form(None), db=Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return HTMLResponse("Post no encontrado", status_code=404)
    post.titulo = titulo
    post.texto = texto
    post.imagen_url = imagen_url
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/editar-horario/{horario_id}")
def actualizar_horario(
    request: Request,
    horario_id: int,
    dia: str = Form(...),
    hora_inicio: str = Form(...),
    hora_fin: str = Form(...),
    actividad: str = Form(...),
    db=Depends(get_db)
):
    horario = db.query(Horario).filter(Horario.id == horario_id).first()
    if not horario:
        return HTMLResponse("Horario no encontrado", status_code=404)
    horario.dia = dia
    horario.hora_inicio = hora_inicio
    horario.hora_fin = hora_fin
    horario.actividad = actividad
    db.commit()
    return RedirectResponse(url="/admin/gestionar-horarios", status_code=HTTP_303_SEE_OTHER)

@app.get("/admin/eliminar-horario/{horario_id}")
def eliminar_horario(horario_id: int, db=Depends(get_db)):
    horario = db.query(Horario).filter(Horario.id == horario_id).first()
    if horario:
        db.delete(horario)
        db.commit()
    return RedirectResponse(url="/admin/gestionar-horarios", status_code=HTTP_303_SEE_OTHER)

@app.get("/admin/publicar-video", response_class=HTMLResponse)
def mostrar_formulario_video(request: Request):
    return templates.TemplateResponse("publicar_video.html", {"request": request})

@app.post("/admin/publicar-video")
def publicar_video(request: Request, title: str = Form(...), url: str = Form(...), plataforma: str = Form(...), db: Session = Depends(get_db)):
    try:
        embed_url = generar_embed(url)
    except Exception:
        return templates.TemplateResponse("publicar_video.html", {
            "request": request,
            "error": "URL inválida o plataforma no soportada."
        })
    nuevo_post = Post(titulo=title, url=url, plataforma=plataforma, embed_url=embed_url, publicado=True)
    db.add(nuevo_post)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/editar/{titulo}")
def editar_seccion_post(request: Request, titulo: str, contenido: str = Form(...), imagen_url: str = Form(None), db=Depends(get_db)):
    seccion = db.query(SeccionInformativa).filter_by(titulo=titulo).first()
    if not seccion:
        raise HTTPException(status_code=404, detail="Sección no encontrada")
    if imagen_url:
        contenido += f'<br><img src="{imagen_url}" alt="Imagen relacionada" style="max-width:100%;">'
    seccion.contenido = contenido
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)