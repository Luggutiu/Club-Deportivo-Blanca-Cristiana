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

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Incluir routers
app.include_router(posts.router, prefix="/posts")
app.include_router(auth.router, prefix="/admin")
app.include_router(admin.router)
app.include_router(dev.router)

from app.routes import info
app.include_router(info.router)

from app.routes import admin_info
app.include_router(admin_info.router)