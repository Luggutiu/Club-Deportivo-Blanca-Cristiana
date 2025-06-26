from fastapi import FastAPI, Request, Depends, Form, HTTPException, Path
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_303_SEE_OTHER
from sqlalchemy.orm import Session

from app.database import engine, Base, SessionLocal
from app.models import Horario, SeccionInformativa, Post
from app.routes import auth, info, admin_info, admin, posts, dev

# Inicialización de la app
app = FastAPI()

# Archivos estáticos y plantillas
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Crear las tablas
Base.metadata.create_all(bind=engine)

# Incluir routers
app.include_router(auth.router)
app.include_router(info.router)
app.include_router(admin_info.router)
app.include_router(admin.router)
app.include_router(posts.router)
app.include_router(dev.router)

# Dependencia de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear secciones por defecto
def crear_secciones_predeterminadas():
    db = SessionLocal()
    secciones = ["mision", "vision", "quienes-somos", "contacto"]
    for titulo in secciones:
        existente = db.query(SeccionInformativa).filter_by(titulo=titulo).first()
        if not existente:
            nueva = SeccionInformativa(titulo=titulo, contenido="")
            db.add(nueva)
    db.commit()
    db.close()

crear_secciones_predeterminadas()

# ------------------------- RUTAS PÚBLICAS -------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.id.desc()).all()
    horarios = db.query(Horario).all()
    secciones_query = db.query(SeccionInformativa).all()
    secciones = {s.titulo: s.contenido for s in secciones_query}
    return templates.TemplateResponse("index.html", {
        "request": request,
        "posts": posts,
        "horarios": horarios,
        "secciones": secciones
    })

@app.get("/test-embed", response_class=HTMLResponse)
def test_embed(request: Request):
    return templates.TemplateResponse("test_embed.html", {"request": request})

# ------------------------- HORARIOS (ADMIN) -------------------------

@app.get("/admin/gestionar-horarios", response_class=HTMLResponse)
def mostrar_formulario_horario(request: Request, db: Session = Depends(get_db)):
    horarios = db.query(Horario).order_by(Horario.dia).all()
    return templates.TemplateResponse("gestionar_horarios.html", {
        "request": request,
        "horarios": horarios
    })

@app.post("/admin/guardar-horario")
def guardar_horario(
    request: Request,
    dia: str = Form(...),
    hora_inicio: str = Form(...),
    hora_fin: str = Form(...),
    actividad: str = Form(...),
    db: Session = Depends(get_db)
):
    nuevo_horario = Horario(
        dia=dia,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        actividad=actividad
    )
    db.add(nuevo_horario)
    db.commit()
    return RedirectResponse(url="/admin/gestionar-horarios", status_code=HTTP_303_SEE_OTHER)

@app.get("/admin/editar-horario/{horario_id}", response_class=HTMLResponse)
def mostrar_formulario_edicion(request: Request, horario_id: int, db: Session = Depends(get_db)):
    horario = db.query(Horario).filter(Horario.id == horario_id).first()
    if not horario:
        return HTMLResponse("Horario no encontrado", status_code=404)
    return templates.TemplateResponse("editar_horario.html", {
        "request": request,
        "horario": horario
    })

@app.post("/admin/editar-horario/{horario_id}")
def actualizar_horario(
    request: Request,
    horario_id: int,
    dia: str = Form(...),
    hora_inicio: str = Form(...),
    hora_fin: str = Form(...),
    actividad: str = Form(...),
    db: Session = Depends(get_db)
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
def eliminar_horario(horario_id: int, db: Session = Depends(get_db)):
    horario = db.query(Horario).filter(Horario.id == horario_id).first()
    if horario:
        db.delete(horario)
        db.commit()
    return RedirectResponse(url="/admin/gestionar-horarios", status_code=HTTP_303_SEE_OTHER)

# ------------------------- PUBLICACIONES -------------------------

@app.post("/admin/eliminar-post/{post_id}")
async def eliminar_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    db.delete(post)
    db.commit()
    return RedirectResponse(url="/admin", status_code=HTTP_303_SEE_OTHER)

