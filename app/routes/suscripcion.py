from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Suscriptor

router = APIRouter()

@router.post("/suscribirse")
def suscribirse(nombre: str = Form(None), correo: str = Form(...), db: Session = Depends(get_db)):
    if db.query(Suscriptor).filter_by(correo=correo).first():
        return RedirectResponse(url="/?error=correo_existe", status_code=303)
    
    nuevo = Suscriptor(nombre=nombre, correo=correo)
    db.add(nuevo)
    db.commit()
    return RedirectResponse(url="/?suscrito=1", status_code=303)

