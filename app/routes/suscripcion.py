from fastapi import APIRouter, Form, File, UploadFile, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import os, shutil, re

from app.database import get_db
from app.models import Suscriptor
from app.utils.email_utils import notificar_admin_suscripcion, enviar_correo_bienvenida

router = APIRouter()

TIPOS_DOCUMENTO_VALIDOS = ["Cédula de ciudadanía", "Tarjeta de identidad", "Cédula de extranjería", "Pasaporte"]

@router.post("/suscribirse")
async def suscribirse_formulario(
    nombre_completo: str = Form(...),
    correo: EmailStr = Form(...),
    tipo_documento: str = Form(...),
    numero_documento: str = Form(...),
    celular: str = Form(...),
    acepto: bool = Form(...),
    archivo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    # Verificación de aceptación
    if not acepto:
        return HTMLResponse(content="Debes aceptar los términos y condiciones.", status_code=400)

    # Validación del nombre
    if not (3 <= len(nombre_completo) <= 100) or re.search(r"\d", nombre_completo):
        return HTMLResponse(
            content="El nombre completo es inválido. No debe contener números y debe tener entre 3 y 100 caracteres.",
            status_code=400
        )

    # Validación del tipo de documento
    if tipo_documento not in TIPOS_DOCUMENTO_VALIDOS:
        return HTMLResponse(content="Tipo de documento no válido.", status_code=400)

    # Validación del número de documento
    if not numero_documento.isdigit() or not (5 <= len(numero_documento) <= 20):
        return HTMLResponse(content="Número de documento inválido. Debe contener solo dígitos y tener entre 5 y 20 caracteres.", status_code=400)

    # Validación del número de celular
    if not re.fullmatch(r"\d{10}", celular):
        return HTMLResponse(content="Número de celular inválido. Debe tener exactamente 10 dígitos.", status_code=400)

    # Verificar duplicado por correo
    if db.query(Suscriptor).filter_by(correo=correo).first():
        return HTMLResponse(content="Este correo ya está registrado.", status_code=400)

    # Validación y guardado del archivo (si existe)
    archivo_path = None
    if archivo:
        if archivo.content_type not in ["application/pdf", "image/jpeg", "image/png"]:
            return HTMLResponse(content="Formato de archivo no permitido. Solo se aceptan PDF, JPG o PNG.", status_code=400)

        max_size = 5 * 1024 * 1024  # 5MB
        contenido = await archivo.read()
        if len(contenido) > max_size:
            return HTMLResponse(content="El archivo excede el tamaño máximo de 5MB.", status_code=400)

        carpeta_temp = "temp_files"
        os.makedirs(carpeta_temp, exist_ok=True)
        archivo_path = os.path.join(carpeta_temp, archivo.filename)
        with open(archivo_path, "wb") as buffer:
            buffer.write(contenido)

    # Crear el nuevo suscriptor
    try:
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
    except IntegrityError:
        db.rollback()
        return HTMLResponse(content="Ya existe un suscriptor con estos datos.", status_code=400)

    # Enviar correos
    await notificar_admin_suscripcion(
        nombre=nombre_completo,
        correo=correo,
        documento=numero_documento,
        tipo=tipo_documento,
        celular=celular,
        archivo_path=archivo_path
    )
    await enviar_correo_bienvenida(nombre_completo, correo)

    # Limpieza
    if archivo_path and os.path.exists(archivo_path):
        os.remove(archivo_path)

    return RedirectResponse(url=f"/confirmacion_suscripcion?nombre={nombre_completo}", status_code=303)