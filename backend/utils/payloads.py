import base64


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
                        "mimeType": part.get("mimeType"),
                        "attachmentId": attachment_id,
                        "size": len(contenido),
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
