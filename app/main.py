from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

'uvicorn app.main:app --reload'

from app.routes import posts

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

from fastapi import Request
from fastapi.responses import RedirectResponse

@app.get("/")
def root(request: Request):
    auth = request.cookies.get("authenticated")
    if auth != "yes":
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("index.html", {"request": request})

app.include_router(posts.router, prefix="/posts")
from app.routes import posts, auth

app.include_router(posts.router, prefix="/posts")
app.include_router(auth.router, prefix="/admin")


from app.database import engine
from app import models

models.Base.metadata.create_all(bind=engine)

from app.routes import auth  # importa la ruta nueva

app.include_router(auth.router)  # incluye el router

from app.routes import admin  # importar el archivo de rutas

app.include_router(admin.router)  # incluir el router