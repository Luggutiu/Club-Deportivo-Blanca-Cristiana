from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
import os

conf = ConnectionConfig (
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
)

async def enviar_correo_bienvenida(destinatario: EmailStr, nombre: str):
    asunto = "¡Bienvenido!"
    cuerpo = f"<h2>Hola {nombre}</h2><p>Gracias por registrarte.</p>"
    mensaje = MessageSchema(
        subject=asunto,
        recipients=[destinatario],
        body=cuerpo,
        subtype="html",
    )
    fm = FastMail(conf)
    await fm.send_message(mensaje)

async def notificar_admin_suscripcion(nombre, correo, documento, tipo, celular):
    asunto = f"Nuevo suscriptor: {nombre}"
    cuerpo = f"""
    <ul>
        <li>Correo: {correo}</li>
        <li>Documento: {tipo} - {documento}</li>
        <li>Celular: {celular}</li>
    </ul>
    """
    mensaje = MessageSchema(
        subject=asunto,
        recipients=["admin@tudominio.com"],
        body=cuerpo,
        subtype="html",
    )
    fm = FastMail(conf)
    await fm.send_message(mensaje)