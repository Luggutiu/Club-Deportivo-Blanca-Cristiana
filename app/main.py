from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import engine, Base
from app.routes import auth, info, admin_info, admin, posts, dev
import os
from fastapi import Form
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Horario

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear tablas en la base de datos (si no existen)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Montar archivos estáticos (CSS, imágenes)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Incluir routers
app.include_router(auth.router)
app.include_router(info.router)
app.include_router(admin_info.router)
app.include_router(admin.router)
app.include_router(posts.router)
app.include_router(dev.router)

from app.models import SeccionInformativa
from app.database import SessionLocal

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



@app.get("/admin/gestionar-horarios", response_class=HTMLResponse)
async def mostrar_formulario_horario(request: Request, db: Session = Depends(get_db)):
    horarios = db.query(Horario).all()
    return templates.TemplateResponse("gestionar_horarios.html", {
        "request": request,
        "horarios": horarios
    })

@app.post("/admin/guardar-horario")
async def guardar_horario(
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
    return RedirectResponse(url="/admin/gestionar-horarios", status_code=303)

from app.models import Post  # asegúrate que esto esté ya importado
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.id.desc()).all()
    horarios = db.query(Horario).all()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "posts": posts,
        "horarios": horarios
    })