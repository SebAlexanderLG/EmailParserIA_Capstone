import json
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi.responses import RedirectResponse
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from .token_service import guardar_token_db
from core.config import SCOPES, CLIENT_SECRETS_FILE
from .gmail_service import obtener_perfil


def auth_load() -> dict:
    """Cargar la configuración del cliente desde el archivo JSON"""
    with open(CLIENT_SECRETS_FILE, encoding="utf-8") as f:
        return json.load(f)


def autorizacion_gmail() -> str:
    """Genera URL de autorización para Gmail OAuth2"""
    flow = google_auth_oauthlib.flow.Flow.from_client_config(auth_load(), scopes=SCOPES)
    flow.redirect_uri = "http://localhost:8000/auth/callback"
    authorization_url, state = flow.authorization_url(
        prompt="consent", access_type="offline", include_granted_scopes="true"
    )
    return authorization_url


def auth_callback(request: Request) -> JSONResponse:
    """Intercambia código de autorización por token y guarda en DB"""
    code: str | None = request.query_params.get("code")
    if not code:
        return JSONResponse(
            content={"error": "No se recibió ningún código de autorización"},
            status_code=400,
        )

    flow = google_auth_oauthlib.flow.Flow.from_client_config(auth_load(), scopes=SCOPES)
    flow.redirect_uri = "http://localhost:8000/auth/callback"
    tokens = flow.fetch_token(code=code)

    creds = flow.credentials

    service = build("gmail", "v1", credentials=creds)
    profile_gmail = service.users().getProfile(userId="me").execute()
    email_usuario = profile_gmail["emailAddress"]

    # Guardar token en DB
    guardar_token_db(tokens)

    perfil = obtener_perfil(email_usuario)
    perfil["nombre_usuario"]

    response = RedirectResponse(url="http://localhost:5173/redirect")

    response.set_cookie(
        key="email",
        value=email_usuario,
        httponly=True,
        secure=False,
        max_age=60 * 60 * 24,
        samesite="lax",
    )

    return response
    # response = guardar_token_db(tokens)
    # return JSONResponse(content=response)
