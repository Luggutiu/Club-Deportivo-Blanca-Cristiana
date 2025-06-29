from fastapi import Form, File, UploadFile, Request, Depends, APIRouter
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os, shutil

from app.database import get_db
from app.models import Suscriptor
from app.utils.email_utils import notificar_admin_suscripcion, enviar_correo_bienvenida

router = APIRouter()

@router.post("/suscribirse")
async def suscribirse_formulario(
    request: Request,
    nombre_completo: str = Form(...),
    correo: str = Form(...),
    tipo_documento: str = Form(...),
    numero_documento: str = Form(...),
    celular: str = Form(...),
    acepto: bool = Form(...),
    archivo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    # Validación de términos
    if not acepto:
        return RedirectResponse(
            url=f"/suscribirse?error=formato_invalido&nombre_completo={nombre_completo}&correo={correo}&tipo_documento={tipo_documento}&numero_documento={numero_documento}&celular={celular}&acepto=true",
            status_code=303
        )

    # Verificar documento duplicado
    documento_existente = db.query(Suscriptor).filter(Suscriptor.numero_documento == numero_documento).first()
    if documento_existente:
        return RedirectResponse(
            url=f"/suscribirse?error=documento_existente&nombre_completo={nombre_completo}&correo={correo}&tipo_documento={tipo_documento}&numero_documento={numero_documento}&celular={celular}&acepto=true",
            status_code=303
        )

    # Guardar archivo temporal si existe
    archivo_path = None
    if archivo:
        carpeta_temp = "temp_files"
        os.makedirs(carpeta_temp, exist_ok=True)
        archivo_path = os.path.join(carpeta_temp, archivo.filename)
        with open(archivo_path, "wb") as buffer:
            shutil.copyfileobj(archivo.file, buffer)

    # Crear objeto
    nuevo_suscriptor = Suscriptor(
        nombre_completo=nombre_completo,
        correo=correo,
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        celular=celular
    )

    # Guardar en DB
    try:
        db.add(nuevo_suscriptor)
        db.commit()
        db.refresh(nuevo_suscriptor)
    except Exception as e:
        db.rollback()
        if archivo_path and os.path.exists(archivo_path):
            os.remove(archivo_path)
        return RedirectResponse(
            url=f"/suscribirse?error=registro_fallido&nombre_completo={nombre_completo}&correo={correo}&tipo_documento={tipo_documento}&numero_documento={numero_documento}&celular={celular}&acepto=true",
            status_code=303
        )

    # Notificación y correo
    await notificar_admin_suscripcion(
        nombre=nombre_completo,
        correo=correo,
        documento=numero_documento,
        tipo=tipo_documento,
        celular=celular,
        archivo_path=archivo_path
    )

    await enviar_correo_bienvenida(correo, nombre_completo)

    return RedirectResponse(
        url="/suscribirse?success=¡Gracias por unirte al club!",
        status_code=303
    )