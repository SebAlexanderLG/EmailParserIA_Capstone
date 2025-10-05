from fastapi import APIRouter
from services.gmail_service import (
    obtener_perfil,
    obtener_correos_preview,
    correo_completo,
)

router = APIRouter(prefix="/gmail", tags=["Gmail"])


@router.post("/perfil_gmail")
def perfil_gmail(email):
    """Obtiene el perfil de Gmail usando el token almacenado y refrescado si es necesario"""
    return obtener_perfil(email)


@router.post("/correosPreview")
def correos_preview(email: str, limit: int = 10, formato: str = "metadata"):
    """Endpoint que trae los ultimos 10 correos en formato preview"""
    return obtener_correos_preview(email=email, limit=limit, format_type=formato)


@router.post("/correos")
def correos(email: str, mensaje_id: str):
    """Endpoint que trae el remitente, asunto y cuerpo del correo"""
    return correo_completo(email=email, mensaje_id=mensaje_id)
