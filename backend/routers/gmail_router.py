from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from googleapiclient.discovery import build
from services.token_service import cargar_credenciales
from services.gmail_service import obtener_correos_preview, correo_completo

router = APIRouter(prefix="/gmail", tags=["Gmail"])


@router.post("/perfil_gmail")
def perfil_gmail(email: str):
    """Obtiene el perfil de Gmail usando el token almacenado y refrescado si es necesario"""
    creds = cargar_credenciales(email=email)
    if not creds:
        return RedirectResponse(url="/")  # No hay token, redirige a autenticarse

    service = build("gmail", "v1", credentials=creds)
    profile = service.users().getProfile(userId="me").execute()
    nombre_usuario = email.split("@")[0]
    return {"profile": profile, "nombre_usuario": nombre_usuario}


@router.post("/correosPreview")
def correos_preview(email: str, limit: int = 10, formato: str = "metadata"):
    return obtener_correos_preview(email=email, limit=limit, format_type=formato)


@router.post("/correos")
def correos(email: str, mensaje_id: str):
    return correo_completo(email=email, mensaje_id=mensaje_id)
