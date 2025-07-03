from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from urllib.parse import urlencode
import httpx
import os

from app.database import get_db
from app.models import Suscriptor
from app.utils.email_utils import enviar_correo_bienvenida, notificar_admin_suscripcion

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Cargar desde variables de entorno (.env)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")  # ej. https://tu-dominio.com/auth/google/callback

@router.get("/auth/google/login")
async def login_via_google():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }

    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return RedirectResponse(google_auth_url)


@router.get("/auth/google/callback")
async def google_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return HTMLResponse("Código no proporcionado", status_code=400)

    token_url = "https://oauth2.googleapis.com/token"
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            token_url,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        token_json = token_response.json()
        access_token = token_json.get("access_token")
        if not access_token:
            return HTMLResponse("Token no recibido", status_code=400)

        user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        user_response = await client.get(
            user_info_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = user_response.json()

    correo = user_data.get("email")
    nombre = user_data.get("name")

    return RedirectResponse(f"/auth/google/register?correo={correo}&nombre={nombre}")


@router.get("/auth/google/register", response_class=HTMLResponse)
def mostrar_formulario_datos(request: Request, correo: str, nombre: str):
    html = f"""
    <html>
    <body style='font-family: sans-serif; max-width: 600px; margin: auto;'>
        <h2>Completa tu registro</h2>
        <form action="/auth/google/complete" method="post">
            <input type="hidden" name="correo" value="{correo}">
            <input type="hidden" name="nombre_completo" value="{nombre}">
            
            <label>Tipo de documento:</label>
            <select name="tipo_documento" required>
                <option value="Cédula">Cédula</option>
                <option value="Cédula de extranjería">Cédula de extranjería</option>
                <option value="Tarjeta de identidad">Tarjeta de identidad</option>
                <option value="Pasaporte">Pasaporte</option>
            </select><br><br>

            <label>Número de documento:</label>
            <input type="text" name="numero_documento" required><br><br>

            <label>Número de celular:</label>
            <input type="text" name="celular" required><br><br>

            <button type="submit">Registrarme</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.post("/auth/google/complete")
async def completar_suscripcion(
    request: Request,
    correo: str = Form(...),
    nombre_completo: str = Form(...),
    tipo_documento: str = Form(...),
    numero_documento: str = Form(...),
    celular: str = Form(...),
    db: Session = Depends(get_db)
):
    existente = db.query(Suscriptor).filter_by(correo=correo).first()
    if existente:
        return HTMLResponse(f"<h3>El correo {correo} ya está registrado.</h3>")

    suscriptor = Suscriptor(
        correo=correo,
        nombre=nombre_completo,
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        nombre_completo=nombre_completo,
        celular=celular
    )
    db.add(suscriptor)
    db.commit()

    await enviar_correo_bienvenida(correo, nombre_completo)
    await notificar_admin_suscripcion(nombre_completo, correo, numero_documento, tipo_documento, celular)

    return HTMLResponse(f"<h3>Gracias por registrarte, {nombre_completo}. Revisa tu correo.</h3>")