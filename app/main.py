from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import posts, auth, admin, dev

from app.database import engine
from app import models

# Crear tablas si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configurar archivos estáticos y templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Ruta raíz redirige a /posts
from fastapi.responses import RedirectResponse
@app.get("/")
def root():
    return RedirectResponse(url="/posts")

# Incluir routers
app.include_router(posts.router, prefix="/posts")
app.include_router(auth.router, prefix="/admin")
app.include_router(admin.router)
app.include_router(dev.router)