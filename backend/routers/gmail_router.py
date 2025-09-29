from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from googleapiclient.discovery import build
from services.token_service import cargar_credenciales

router = APIRouter()


@router.post("/perfil_gmail")
def perfil_gmail(email: str):
    """Obtiene el perfil de Gmail usando el token almacenado y refrescado si es necesario"""
    creds = cargar_credenciales(email=email)
    if not creds:
        return RedirectResponse(url="/")  # No hay token, redirige a autenticarse

    service = build("gmail", "v1", credentials=creds)
    profile = service.users().getProfile(userId="me").execute()
    nombre_usuario = email.split("@")[0]
    return profile, nombre_usuario
