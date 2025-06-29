from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Suscriptor
from app.utils.email_utils import enviar_correo_bienvenida, notificar_admin_suscripcion
from fastapi.templating import Jinja2Templates
from fastapi import UploadFile, File
import shutil
import os
import uuid

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
    acepto: bool = Form(...),
    foto: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    if not acepto:
        return HTMLResponse("<h3>Debes aceptar los términos y condiciones.</h3>")

    existente = db.query(Suscriptor).filter_by(correo=correo).first()
    if existente:
        return HTMLResponse(f"<h3>El correo {correo} ya está registrado.</h3>")

    suscriptor = Suscriptor(
        correo=correo,
        nombre_completo=nombre_completo,
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        celular=celular
    )
    db.add(suscriptor)
    db.commit()

    # Guardar archivo temporalmente
    foto_path = None
    if foto:
        extension = foto.filename.split(".")[-1]
        filename = f"foto_{uuid.uuid4()}.{extension}"
        foto_path = os.path.join("temp", filename)
        os.makedirs("temp", exist_ok=True)
        with open(foto_path, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)

    # Notificar al admin con la imagen adjunta
    await notificar_admin_suscripcion(
        nombre_completo, correo, numero_documento, tipo_documento, celular, foto_path
    )

    # Correo de bienvenida (sin adjunto)
    await enviar_correo_bienvenida(correo, nombre_completo)

    # Borrar archivo temporal si existe
    if foto_path and os.path.exists(foto_path):
        os.remove(foto_path)

    return templates.TemplateResponse("confirmacion_suscripcion.html", {"request": request, "nombre": nombre_completo})