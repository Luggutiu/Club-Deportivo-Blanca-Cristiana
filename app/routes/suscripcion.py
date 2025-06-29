from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Suscriptor
from app.utils.email_utils import enviar_correo_bienvenida, notificar_admin_suscripcion
from fastapi.templating import Jinja2Templates

router = APIRouter()




templates = Jinja2Templates(directory="app/templates")

@router.post("/suscribirse", response_class=HTMLResponse)
async def suscribirse_formulario(
    request: Request,
    nombre_completo: str = Form(...),
    correo: str = Form(...),
    tipo_documento: str = Form(...),
    numero_documento: str = Form(...),
    celular: str = Form(...),
    acepta_politica: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verificar duplicado por correo
    if db.query(Suscriptor).filter_by(correo=correo).first():
        return HTMLResponse("<h3>Este correo ya está registrado.</h3>", status_code=400)

    # Verificar duplicado por número de documento
    if db.query(Suscriptor).filter_by(numero_documento=numero_documento).first():
        return HTMLResponse("<h3>Este documento ya está registrado.</h3>", status_code=400)

    nuevo = Suscriptor(
        nombre_completo=nombre_completo,
        correo=correo,
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        celular=celular
    )
    db.add(nuevo)
    db.commit()

    await enviar_correo_bienvenida(correo, nombre_completo)
    await notificar_admin_suscripcion(nombre_completo, correo, numero_documento, tipo_documento, celular)

    return templates.TemplateResponse("confirmacion_suscripcion.html", {
        "request": request,
        "nombre": nombre_completo
    })