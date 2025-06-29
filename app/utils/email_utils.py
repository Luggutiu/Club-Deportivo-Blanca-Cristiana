from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
import os
import shutil
import mimetypes

# Configuración de FastAPI-Mail con variables de entorno
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
async def enviar_correo_bienvenida(nombre: str, destinatario: EmailStr):
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
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(mensaje)

# Correo de notificación al administrador con posible archivo adjunto
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

    attachments = []

    if archivo_path and os.path.exists(archivo_path):
        # Validar tamaño del archivo (ej. máximo 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if os.path.getsize(archivo_path) <= max_size:
            mime_type, _ = mimetypes.guess_type(archivo_path)
            with open(archivo_path, "rb") as f:
                contenido = f.read()
                attachments.append({
                    "file": contenido,
                    "filename": os.path.basename(archivo_path),
                    "mime_type": mime_type or "application/octet-stream"
                })
        else:
            print("Archivo excede el tamaño permitido y no será adjuntado.")

    mensaje = MessageSchema(
        subject=asunto,
        recipients=["clubdeportivoblancacristiana@gmail.com"],
        body=cuerpo,
        subtype=MessageType.html,
        attachments=attachments
    )

    fm = FastMail(conf)
    await fm.send_message(mensaje)

    # Eliminar archivo después de enviar
    if archivo_path and os.path.exists(archivo_path):
        os.remove(archivo_path)