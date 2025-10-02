from email.utils import parsedate_to_datetime
import re
import base64


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


def procesar_payload(payload: dict, service, mensaje_id: str):
    """Procesa cada payload y lo trae"""
    cuerpo_texto = ""
    cuerpo_html = ""
    adjuntos = []

    def recorrer_payload(parts: list):
        nonlocal cuerpo_texto, cuerpo_html, adjuntos
        for part in parts:
            mime_type = part.get("mimeType", "")
            body = part.get("body", {})
            data = body.get("data")
            attachment_id = body.get("attachmentId")
            filename = part.get("filename", "")

            if mime_type == "text/plain" and data:
                cuerpo_texto += base64.urlsafe_b64decode(data).decode(
                    "utf-8", errors="ignore"
                )
            elif mime_type == "text/html" and data:
                cuerpo_html += base64.urlsafe_b64decode(data).decode(
                    "utf-8", errors="ignore"
                )
            elif attachment_id:
                attachment = (
                    service.users()
                    .messages()
                    .attachments()
                    .get(userId="me", messageId=mensaje_id, id=attachment_id)
                    .execute()
                )
                contenido = base64.urlsafe_b64decode(attachment["data"])
                adjuntos.append(
                    {
                        "filename": filename,
                        "size": len(contenido),
                        "mimeType": part.get("mimeType"),
                    }
                )
            elif "parts" in part:
                recorrer_payload(part["parts"])

    if "parts" in payload:
        recorrer_payload(payload["parts"])
    else:
        body = payload.get("body", {})
        data = body.get("data")
        if data:
            cuerpo_texto = base64.urlsafe_b64decode(data).decode(
                "utf-8", errors="ignore"
            )
    return cuerpo_texto, cuerpo_html, adjuntos
