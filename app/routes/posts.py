from fastapi import APIRouter
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.database import SessionLocal
from app import models
from app.embedder import generar_embed

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def read_posts(request: Request):
    db = SessionLocal()
    posts = db.query(models.Post).all()
    db.close()

    embedded_posts = []
    for post in posts:
        embed_url, platform = generar_embed(post.url)
        embedded_posts.append({
            "title": post.title,
            "embed_url": embed_url,
            "platform": platform
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "posts": embedded_posts
    })
