import json
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import Request
import google.oauth2.id_token
from google.auth.transport import requests
import google_auth_oauthlib.flow
from core.config import SCOPES, CLIENT_SECRETS_FILE
from .token_service import guardar_token_db


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

    # Guardar token en DB
    response = guardar_token_db(tokens)
    return JSONResponse(content=response)
