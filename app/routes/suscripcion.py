from fastapi import APIRouter, Form, File, UploadFile, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import os, shutil

from app.database import get_db
from app.models import Suscriptor
from app.utils.email_utils import notificar_admin_suscripcion, enviar_correo_bienvenida

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
        return JSONResponse(status_code=400, content={"error": "Debes aceptar los términos y condiciones."})

    # Validar que el número de documento no esté registrado
    documento_existente = db.query(Suscriptor).filter(Suscriptor.numero_documento == numero_documento).first()
    if documento_existente:
        return JSONResponse(status_code=400, content={"error": "documento_existente"})

    # Guardar archivo temporal si se cargó
    archivo_path = None
    if archivo:
        carpeta_temp = "temp_files"
        os.makedirs(carpeta_temp, exist_ok=True)
        archivo_path = os.path.join(carpeta_temp, archivo.filename)
        with open(archivo_path, "wb") as buffer:
            shutil.copyfileobj(archivo.file, buffer)

    # Guardar suscriptor
    nuevo_suscriptor = Suscriptor(
        nombre_completo=nombre_completo,
        correo=correo,
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        celular=celular
    )

    try:
        db.add(nuevo_suscriptor)
        db.commit()
        db.refresh(nuevo_suscriptor)
    except Exception as e:
        db.rollback()
        if archivo_path and os.path.exists(archivo_path):
            os.remove(archivo_path)
        return JSONResponse(status_code=500, content={"error": "registro_fallido"})

    # Enviar correos
    await notificar_admin_suscripcion(
        nombre=nombre_completo,
        correo=correo,
        documento=numero_documento,
        tipo=tipo_documento,
        celular=celular,
        archivo_path=archivo_path
    )

    await enviar_correo_bienvenida(correo, nombre_completo)

    return JSONResponse(content={"mensaje": "¡Suscripción exitosa!"})
