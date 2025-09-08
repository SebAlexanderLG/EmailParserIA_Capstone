import google_auth_oauthlib.flow
import json
from core.config import SCOPES, CLIENT_SECRETS_FILE
from fastapi.responses import RedirectResponse


def auth_load() -> dict:
    """Función para cargar la configuración del cliente desde el archivo JSON."""
    with open(CLIENT_SECRETS_FILE, encoding="utf-8") as f:
        return json.load(f)


def autorizacion_gmail() -> RedirectResponse:
    """Función para iniciar la autenticación con Gmail"""
    flow = google_auth_oauthlib.flow.Flow.from_client_config(auth_load(), scopes=SCOPES)
    flow.redirect_uri = "http://localhost:8000/auth/callback"
    authorization_url = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )
    return RedirectResponse(authorization_url)
