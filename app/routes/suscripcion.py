from fastapi import APIRouter, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Suscriptor

router = APIRouter()

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/suscribirse")
async def mostrar_formulario(request: Request):
    return templates.TemplateResponse("suscribirse.html", {"request": request})

@router.post("/suscribirse")
def suscribirse(
    tipo_documento: str = Form(...),
    numero_documento: str = Form(...),
    nombre_completo: str = Form(...),
    celular: str = Form(...),
    correo: str = Form(...),
    db: Session = Depends(get_db)
):
    existe_correo = db.query(Suscriptor).filter_by(correo=correo).first()
    existe_documento = db.query(Suscriptor).filter_by(numero_documento=numero_documento).first()

    if existe_correo or existe_documento:
        return RedirectResponse(url="/suscribirse?error=existe", status_code=303)

    nuevo_suscriptor = Suscriptor(
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        nombre_completo=nombre_completo,
        celular=celular,
        correo=correo
    )
    db.add(nuevo_suscriptor)
    db.commit()

    return RedirectResponse(url="/suscribirse?suscrito=1", status_code=303)