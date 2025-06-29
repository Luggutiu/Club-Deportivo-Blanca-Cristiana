from fastapi import APIRouter, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Suscriptor

router = APIRouter()

@router.post("/suscribirse")
def suscribirse(
    nombre: str = Form(...),
    correo: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verificar si ya existe el correo
    if db.query(Suscriptor).filter_by(correo=correo).first():
        return RedirectResponse(url="/?error=correo_existe", status_code=303)

    # Crear nuevo suscriptor con datos mínimos
    nuevo = Suscriptor(
        nombre_completo=nombre,
        correo=correo,
        tipo_documento="Sin especificar",
        numero_documento="0000",
        celular="0000000000"
    )
    db.add(nuevo)
    db.commit()

    return RedirectResponse(url="/?suscrito=1", status_code=303)