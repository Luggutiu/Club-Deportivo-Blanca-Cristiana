from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
from typing import Optional
import os

conf = ConnectionConfig(
    MAIL_USERNAME="tu-correo@gmail.com",
    MAIL_PASSWORD="tu-clave-o-app-password",
    MAIL_FROM="tu-correo@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="Club Deportivo Blanca Cristiana",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER="app/templates"
)

async def notificar_admin_suscripcion(
    nombre: str,
    correo: str,
    documento: str,
    tipo: str,
    celular: str,
    ruta_foto: Optional[str] = None
):
    asunto = f"Nuevo suscriptor: {nombre}"

    cuerpo_html = f"""
    <h2>Nuevo suscriptor</h2>
    <ul>
        <li><strong>Nombre:</strong> {nombre}</li>
        <li><strong>Correo:</strong> {correo}</li>
        <li><strong>Tipo de documento:</strong> {tipo}</li>
        <li><strong>Número de documento:</strong> {documento}</li>
        <li><strong>Celular:</strong> {celular}</li>
    </ul>
    """

    attachments = None
    if ruta_foto and os.path.exists(ruta_foto):
        with open(ruta_foto, "rb") as f:
            file_data = f.read()
        attachments = [{
            "file": file_data,
            "filename": os.path.basename(ruta_foto),
            "mime_type": "image/jpeg" if ruta_foto.endswith(".jpg") or ruta_foto.endswith(".jpeg") else "image/png"
        }]

    mensaje = MessageSchema(
        subject=asunto,
        recipients=["clubdeportivoblancacristiana@gmail.com"],
        body=cuerpo_html,
        subtype=MessageType.html,
        attachments=attachments
    )

    fm = FastMail(conf)
    await fm.send_message(mensaje)