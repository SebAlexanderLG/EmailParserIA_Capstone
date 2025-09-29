from googleapiclient.discovery import build
from .token_service import cargar_credenciales


def obtener_mensajes(email: str | None = None):
    creds = cargar_credenciales(email)
    if not creds:
        return None
    service = build("gmail", "v1", credentials=creds)
    result = service.users().messages().list(userId="me").execute()
    return result.get("messages", [])
