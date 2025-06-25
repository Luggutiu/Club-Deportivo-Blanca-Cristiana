from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.embedder import generar_embed
from app.database import SessionLocal
from app import models

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    db = SessionLocal()
    posts = db.query(models.Post).all()
    db.close()
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})