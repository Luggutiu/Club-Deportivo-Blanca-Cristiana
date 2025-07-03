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
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

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
    <!DOCTYPE html>
    <html lang=\"es\">
    <head>
        <meta charset=\"UTF-8\">
        <title>Completa tu registro - Club Deportivo Blanca Cristiana</title>
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
        <link rel=\"stylesheet\" href=\"/static/styles.css\">
        <style>
            body {{ background-color: #0e0e0e; color: white; font-family: 'Segoe UI', sans-serif; padding: 2rem; }}
            .form-card {{ max-width: 600px; margin: auto; background-color: #1e1e1e; padding: 2rem; border-radius: 12px; box-shadow: 0 0 15px rgba(255, 105, 180, 0.2); }}
            input, select {{ width: 100%; padding: 0.7rem; margin-top: 0.5rem; margin-bottom: 1.5rem; border: none; border-radius: 8px; background-color: #2c2c2c; color: white; }}
            label {{ font-weight: bold; }}
            button {{ background-color: #ff5e78; color: white; padding: 0.8rem 1.2rem; border: none; border-radius: 8px; font-weight: bold; width: 100%; cursor: pointer; transition: background-color 0.3s ease; }}
            button:hover {{ background-color: #ff2c4d; }}
            a.volver {{ display: inline-block; margin-bottom: 2rem; color: #ff5e78; text-decoration: none; font-weight: bold; }}
        </style>
    </head>
    <body>
        <a href=\"/\" class=\"volver\">⬅ Ir al inicio</a>
        <div class=\"form-card\">
            <h1 style=\"color: #ff5e78;\">Completa tu registro</h1>
            <p>Gracias, <strong>{nombre}</strong> (<span style=\"color:#ccc;\">{correo}</span>). Solo faltan unos datos para finalizar:</p>
            <form action=\"/auth/google/complete\" method=\"post\" enctype=\"multipart/form-data\">
                <input type=\"hidden\" name=\"correo\" value=\"{correo}\">
                <input type=\"hidden\" name=\"nombre_completo\" value=\"{nombre}\">
                <label for=\"tipo_documento\">Tipo de documento:</label>
                <select id=\"tipo_documento\" name=\"tipo_documento\" required>
                    <option value=\"\">Selecciona una opción</option>
                    <option value=\"Cédula\">Cédula</option>
                    <option value=\"Cédula de extranjería\">Cédula de extranjería</option>
                    <option value=\"Tarjeta de identidad\">Tarjeta de identidad</option>
                    <option value=\"Pasaporte\">Pasaporte</option>
                </select>
                <label for=\"numero_documento\">Número de documento:</label>
                <input type=\"text\" id=\"numero_documento\" name=\"numero_documento\" required pattern=\"\\d{{6,15}}\" placeholder=\"Ej: 1234567890\">
                <label for=\"celular\">Número de celular:</label>
                <input type=\"text\" id=\"celular\" name=\"celular\" required pattern=\"3\\d{{9}}\" placeholder=\"Ej: 3001234567\">
                <label for=\"archivo\">Adjuntar foto para carnet:</label>
                <input type=\"file\" name=\"archivo\" accept=\".jpg,.jpeg,.png,.pdf\" required>
                <button type=\"submit\">Registrarme</button>
            </form>
        </div>
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
    # Validar si el número de documento ya está registrado
    doc_existente = db.query(Suscriptor).filter_by(numero_documento=numero_documento).first()
    if doc_existente:
        return HTMLResponse(f"<h3>El número de documento {numero_documento} ya está registrado.</h3>")

    suscriptor = Suscriptor(
        correo=correo,
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        nombre_completo=nombre_completo,
        celular=celular
    )
    db.add(suscriptor)
    db.commit()

    await enviar_correo_bienvenida(correo, nombre_completo)
    await notificar_admin_suscripcion(nombre_completo, correo, numero_documento, tipo_documento, celular)

    return templates.TemplateResponse("confirmacion_suscripcion.html", {
        "request": request,
        "nombre": nombre_completo
    })