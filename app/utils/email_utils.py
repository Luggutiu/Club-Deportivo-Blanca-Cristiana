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
from email_validator import validate_email, EmailNotValidError

async def enviar_correo_bienvenida(destinatario: str, nombre: str):
    try:
        # Validación de correo
        validate_email(destinatario)

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

    except EmailNotValidError as e:
        print(f"❌ Correo inválido: {e}")


# -----------------------------------------------------
# 📩 Correo al administrador con adjunto opcional
# -----------------------------------------------------
from email_validator import validate_email, EmailNotValidError

async def notificar_admin_suscripcion(
    nombre: str,
    correo: str,
    documento: str,
    tipo: str,
    celular: str,
    archivo_path: str = None,
    archivo_bytes: bytes = None,
    archivo_nombre: str = None
):
    try:
        # Validar correo del suscriptor
        validate_email(correo)

        asunto = f"Nuevo suscriptor: {nombre}"
        cuerpo = f"""
        <h2>📩 Nuevo suscriptor</h2>
        <ul>
            <li><strong>Nombre:</strong> {nombre}</li>
            <li><strong>Correo:</strong> {correo}</li>
            <li><strong>Tipo de documento:</strong> {tipo}</li>
            <li><strong>Número de documento:</strong> {documento}</li>
            <li><strong>Celular:</strong> {celular}</li>
        </ul>
        """

        # Adjuntos: siempre enviar una lista, aunque esté vacía
        attachments = []

        if archivo_bytes and archivo_nombre:
            attachments.append({
                "file": archivo_bytes,
                "filename": archivo_nombre,
                "mime_type": "application/octet-stream"
            })
        elif archivo_path and os.path.isfile(archivo_path):
            attachments.append(archivo_path)

        # Construir mensaje
        mensaje = MessageSchema(
            subject=asunto,
            recipients=["clubdeportivoblancacristiana@gmail.com"],
            body=cuerpo,
            subtype="html",
            attachments=attachments
        )

        fm = FastMail(conf)
        await fm.send_message(mensaje)
        print("✅ Notificación enviada al administrador.")

    except EmailNotValidError as e:
        print(f"❌ Correo del suscriptor inválido: {correo} | {e}")

    except Exception as e:
        print(f"❌ Error al enviar notificación al admin: {e}")

    finally:
        # Eliminar archivo temporal si existe
        if archivo_path and os.path.isfile(archivo_path):
            try:
                os.remove(archivo_path)
                print(f"🗑️ Archivo temporal eliminado: {archivo_path}")
            except Exception as err:
                print(f"⚠️ No se pudo eliminar el archivo: {err}")