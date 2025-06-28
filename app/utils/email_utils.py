from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

conf = ConnectionConfig(
    MAIL_USERNAME="clubdeportivoblancacristiana@gmail.com",
    MAIL_PASSWORD="mqwghyheyjxlisyh",
    MAIL_FROM="clubdeportivoblancacristiana@gmail.com",
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