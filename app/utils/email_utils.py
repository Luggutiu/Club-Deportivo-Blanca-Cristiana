from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi import UploadFile
from starlette.requests import Request
from pydantic import EmailStr
import os
import shutil

# Configuración desde variables de entorno
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="Club Deportivo Blanca Cristiana",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER="app/templates"
)

# Correo de bienvenida al suscriptor
async def notificar_admin_suscripcion(nombre: str, correo: str, documento: str, tipo: str, celular: str, archivo_path: str = None):
    asunto = f"Nuevo suscriptor: {nombre}"
    cuerpo = f"""
    <h2>Nuevo suscriptor</h2>
    <ul>
        <li><strong>Nombre:</strong> {nombre}</li>
        <li><strong>Correo:</strong> {correo}</li>
        <li><strong>Tipo de documento:</strong> {tipo}</li>
        <li><strong>Número de documento:</strong> {documento}</li>
        <li><strong>Celular:</strong> {celular}</li>
    </ul>
    """

    attachments = []
    if archivo_path and os.path.exists(archivo_path):
        with open(archivo_path, "rb") as f:
            contenido = f.read()
            ext = archivo_path.split(".")[-1]
            attachments.append(
                {
                    "file": contenido,
                    "filename": os.path.basename(archivo_path),
                    "mime_type": f"application/{ext}" if ext != "jpg" else "image/jpeg"
                }
            )

    mensaje = MessageSchema(
        subject=asunto,
        recipients=["clubdeportivoblancacristiana@gmail.com"],
        body=cuerpo,
        subtype="html",
        attachments=attachments
    )

    fm = FastMail(conf)
    await fm.send_message(mensaje)

    # Limpieza: borrar el archivo temporal
    if archivo_path and os.path.exists(archivo_path):
        os.remove(archivo_path)
        
        # Correo de bienvenida al suscriptor
async def enviar_correo_bienvenida(nombre: str, correo: EmailStr):
    asunto = "¡Bienvenido al Club Deportivo Blanca Cristiana!"
    cuerpo = f"""
    <h2>Hola {nombre},</h2>
    <p>Gracias por suscribirte al Club Deportivo Blanca Cristiana.</p>
    <p>Nos alegra tenerte con nosotros. Pronto recibirás noticias y novedades del club.</p>
    <p>Saludos deportivos,</p>
    <strong>Club Deportivo Blanca Cristiana</strong>
    """

    mensaje = MessageSchema(
        subject=asunto,
        recipients=[correo],
        body=cuerpo,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(mensaje)