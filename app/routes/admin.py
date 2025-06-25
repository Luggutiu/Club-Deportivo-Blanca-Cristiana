from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import SessionLocal
from app.models import Post
from app.utils.embedder import generar_embed

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/admin")
def admin_panel(request: Request):
    db = SessionLocal()
    publicaciones = db.query(Post).order_by(Post.id.desc()).all()
    db.close()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "publicaciones": publicaciones
    })

@router.post("/admin/publicar")
def crear_post(request: Request, url: str = Form(...)):
    db = SessionLocal()
    embed_url, plataforma = generar_embed(url)
    nuevo_post = Post(url=url, embed_url=embed_url, plataforma=plataforma)
    db.add(nuevo_post)
    db.commit()
    db.close()
    return RedirectResponse(url="/admin", status_code=302)