from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
import os

# Validar existencia de variables necesarias
required_envs = ["MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_FROM"]
missing = [key for key in required_envs if not os.getenv(key)]
if missing:
    raise RuntimeError(f"❌ Faltan variables de entorno para el correo: {missing}")

# Configuración SMTP
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

# ------------------------------------------
# 📧 Correo de bienvenida al suscriptor
# ------------------------------------------
async def enviar_correo_bienvenida(destinatario: EmailStr, nombre: str):
    asunto = "¡Bienvenido al Club Deportivo Blanca Cristiana!"
    cuerpo = f"""
    <h2>Hola {nombre},</h2>
    <p>Gracias por suscribirte al <strong>Club Deportivo Blanca Cristiana</strong>.</p>
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
    print(f"✅ Correo de bienvenida enviado a {destinatario}")


# -----------------------------------------------------
# 📩 Correo al administrador con adjunto opcional
# -----------------------------------------------------
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
    <h2>Nuevo suscriptor registrado</h2>
    <p>Se ha registrado un nuevo miembro en el Club Deportivo:</p>
    <ul>
        <li><strong>Nombre completo:</strong> {nombre}</li>
        <li><strong>Correo electrónico:</strong> {correo}</li>
        <li><strong>Tipo de documento:</strong> {tipo}</li>
        <li><strong>Número de documento:</strong> {documento}</li>
        <li><strong>Celular:</strong> {celular}</li>
    </ul>
    <p>Este mensaje ha sido generado automáticamente.</p>
    """

    # Adjuntar solo si se proporcionó
    attachments = [archivo_path] if archivo_path and os.path.isfile(archivo_path) else None

    mensaje = MessageSchema(
        subject=asunto,
        recipients=["clubdeportivoblancacristiana@gmail.com"],
        body=cuerpo,
        subtype="html",
        attachments=attachments
    )

    fm = FastMail(conf)
    await fm.send_message(mensaje)
    print(f"📬 Notificación enviada al administrador sobre {nombre}")

    # Eliminar archivo temporal si existe
    if archivo_path and os.path.isfile(archivo_path):
        os.remove(archivo_path)
        print(f"🗑️ Archivo temporal eliminado: {archivo_path}")