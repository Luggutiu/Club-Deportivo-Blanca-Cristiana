from fastapi import APIRouter, Request, Form, UploadFile, File, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Suscriptor
from app.utils.email_utils import enviar_correo_bienvenida, notificar_admin_suscripcion
import os
import shutil

router = APIRouter()

@router.post("/suscribirse")
async def suscribirse_formulario(
    nombre_completo: str = Form(...),
    correo: str = Form(...),
    tipo_documento: str = Form(...),
    numero_documento: str = Form(...),
    celular: str = Form(...),
    acepto: bool = Form(...),
    archivo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    if not acepto:
        return {"error": "Debes aceptar los términos y condiciones."}

    # ✅ Verificar si el correo ya está registrado
    existente = db.query(Suscriptor).filter(Suscriptor.correo == correo).first()
    if existente:
        return RedirectResponse(url="/suscribirse?error=correo_existente", status_code=303)

    # Guardar archivo temporal si se cargó
    archivo_path = None
    if archivo:
        carpeta_temp = "temp_files"
        os.makedirs(carpeta_temp, exist_ok=True)
        archivo_path = os.path.join(carpeta_temp, archivo.filename)
        with open(archivo_path, "wb") as buffer:
            shutil.copyfileobj(archivo.file, buffer)

    # Crear nuevo suscriptor
    nuevo_suscriptor = Suscriptor(
        nombre_completo=nombre_completo,
        correo=correo,
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        celular=celular
    )
    db.add(nuevo_suscriptor)
    db.commit()
    db.refresh(nuevo_suscriptor)

    # Notificar al admin
    await notificar_admin_suscripcion(
        nombre=nombre_completo,
        correo=correo,
        documento=numero_documento,
        tipo=tipo_documento,
        celular=celular,
        archivo_path=archivo_path
    )

    # Enviar correo al suscriptor
    await enviar_correo_bienvenida(nombre_completo, correo)

    # Eliminar archivo temporal
    if archivo_path and os.path.exists(archivo_path):
        os.remove(archivo_path)

    return RedirectResponse(url="/confirmacion_suscripcion", status_code=303)