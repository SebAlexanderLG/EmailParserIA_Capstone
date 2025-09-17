import google_auth_oauthlib.flow
import json
from core.config import SCOPES, CLIENT_SECRETS_FILE


def auth_load() -> dict:
    """Función para cargar la configuración del cliente desde el archivo JSON."""
    with open(CLIENT_SECRETS_FILE, encoding="utf-8") as f:
        return json.load(f)


def autorizacion_gmail() -> str:
    flow = google_auth_oauthlib.flow.Flow.from_client_config(auth_load(), scopes=SCOPES)
    # Cambiar URI de redirección a localhost para desarrollo local
    flow.redirect_uri = "http://localhost:8000/auth/callback"
    # Cambiar URI de redirección a la URL de Template de React o Django
    # flow.redirect_uri =

    authorization_url, state = flow.authorization_url(
        prompt="consent", access_type="offline", include_granted_scopes="true"
    )
    print("Por favor, ve a este enlace: {}".format(authorization_url))

    return authorization_url
