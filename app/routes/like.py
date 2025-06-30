from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.models import Post
from app.database import get_db

router = APIRouter()

@router.post("/like/{post_id}")
def like_post(post_id: int, request: Request, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")

    post.likes = (post.likes or 0) + 1
    db.commit()
    return RedirectResponse(url="/", status_code=303)