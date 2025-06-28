# auth_google.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse
import httpx

router = APIRouter()

# Reemplaza estos valores con los tuyos
GOOGLE_CLIENT_ID = "TU_CLIENT_ID"
GOOGLE_CLIENT_SECRET = "TU_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:8000/auth/google/callback"

# Configuración OAuth
config = Config(".env")

@router.get("/auth/google/login")
async def login_via_google():
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=openid%20email%20profile"
    )
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

        # Obtener datos del usuario
        user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        user_response = await client.get(
            user_info_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        user_data = user_response.json()
        email = user_data.get("email")
        name = user_data.get("name")

        # Puedes guardar al usuario en la base de datos aquí si lo deseas

        return HTMLResponse(f"Gracias por suscribirte, {name} ({email})")


# En tu main.py (o donde crees la app):
# app.add_middleware(SessionMiddleware, secret_key="tu_clave_secreta")
# app.include_router(router)
