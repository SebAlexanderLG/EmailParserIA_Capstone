import re
from email.utils import parsedate_to_datetime


def extraer_encabezados(payload: dict) -> list:
    """Extrae todos los headers de un correo (From, To, Subject, Message-id, etc.)"""
    return payload.get("headers", [])


def extraer_asunto(headers: list) -> str:
    """Recorre cada header del payload y trae el asunto"""
    return next((h["value"] for h in headers if h["name"] == "Subject"), "")


def extraer_remitente(headers: list) -> str:
    """Recorre cada header del payload y trae el Remitente"""
    remitente = next((h["value"] for h in headers if h["name"] == "From"), "")
    if match := re.search(r"<(.+?)>", remitente):
        return match[1]
    return remitente


def extraer_fecha_correo(headers: list) -> str:
    """Obtiene la fecha del correo"""
    fecha = next((h["value"] for h in headers if h["name"] == "Date"), "")
    if not fecha:
        return ""
    try:
        parser_fecha = parsedate_to_datetime(fecha)
        return parser_fecha.strftime("%d-%m-%Y %H:%M")
    except ImportError:
        return fecha
