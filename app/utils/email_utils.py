from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
import os

# Configuración de FastAPI-Mail
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

# Correo de bienvenida
async def enviar_correo_bienvenida(destinatario: EmailStr, nombre: str):
    asunto = "¡Bienvenido al Club Deportivo Blanca Cristiana!"
    cuerpo = f"""
    <h2>Hola {nombre},</h2>
    <p>Gracias por suscribirte al Club Deportivo Blanca Cristiana.</p>
    <p>Pronto recibirás noticias, eventos y actualizaciones del club.</p>
    <br>
    <p>¡Nos alegra tenerte con nosotros!</p>
    """

    mensaje = MessageSchema(
        subject=asunto,
        recipients=[destinatario],
        body=cuerpo,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(mensaje)

# Correo al administrador con archivo adjunto opcional
async def notificar_admin_suscripcion(
    nombre: str,
    correo: str,
    documento: str,
    tipo: str,
    celular: str,
    archivo_path: str = None
):
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

    # Asegúrate de que sea string si se incluye
    attachments = [str(archivo_path)] if archivo_path and os.path.exists(archivo_path) else []

    mensaje = MessageSchema(
        subject=asunto,
        recipients=["clubdeportivoblancacristiana@gmail.com"],
        body=cuerpo,
        subtype="html",
        attachments=attachments
    )

    fm = FastMail(conf)
    await fm.send_message(mensaje)

    # Eliminar archivo temporal después del envío
    if archivo_path and os.path.exists(archivo_path):
        os.remove(archivo_path)