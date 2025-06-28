from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
import os

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,       # ← Reemplaza MAIL_TLS
    MAIL_SSL_TLS=False,       # ← Reemplaza MAIL_SSL
    USE_CREDENTIALS=True,
)

async def enviar_correo_bienvenida(destinatario: EmailStr, nombre: str):
    asunto = "¡Bienvenido al Club Deportivo Blanca Cristiana!"
    cuerpo = f"""
    <h2>Hola {nombre},</h2>
    <p>Gracias por suscribirte al Club Deportivo Blanca Cristiana.</p>
    <p>Nos alegra contar contigo.</p>
    """

    mensaje = MessageSchema(
        subject=asunto,
        recipients=[destinatario],
        body=cuerpo,
        subtype="html",
    )

    fm = FastMail(conf)
    await fm.send_message(mensaje)

async def notificar_admin_suscripcion(nombre: str, correo: str, documento: str, tipo: str, celular: str):
    asunto = f"Nuevo suscriptor: {nombre}"
    cuerpo = f"""
    <h2>Nuevo suscriptor vía Google</h2>
    <ul>
        <li><strong>Nombre:</strong> {nombre}</li>
        <li><strong>Correo:</strong> {correo}</li>
        <li><strong>Tipo de documento:</strong> {tipo}</li>
        <li><strong>Número de documento:</strong> {documento}</li>
        <li><strong>Celular:</strong> {celular}</li>
    </ul>
    """

    mensaje = MessageSchema(
        subject=asunto,
        recipients=["clubdeportivoblancacristiana@gmail.com"],  # ← Cambia este por el tuyo
        body=cuerpo,
        subtype="html",
    )

    fm = FastMail(conf)
    await fm.send_message(mensaje)