from io import BytesIO
from base64 import urlsafe_b64decode
from fastapi.responses import StreamingResponse
from googleapiclient.discovery import build
from fastapi import HTTPException


def descargar_adjunto_gmail(
    email: str, mensaje_id: str, attachment_id: str, filename: str = None
):
    """Función que permite descargar archivos adjuntos que estén en un correo."""

    from services.token_service import cargar_credenciales

    creds = cargar_credenciales(email=email)
    if not creds:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    service = build("gmail", "v1", credentials=creds)

    try:
        adjunto = (
            service.users()
            .messages()
            .attachments()
            .get(userId="me", messageId=mensaje_id, id=attachment_id)
            .execute()
        )

        data = adjunto.get("data")
        if not data:
            raise HTTPException(status_code=404, detail="Adjunto vacío")

        contenido = urlsafe_b64decode(data)
        archivo = BytesIO(contenido)

        nombre_archivo = filename or f"archivo_{attachment_id}.bin"

        return StreamingResponse(
            archivo,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{nombre_archivo}"'},
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Error descargando el adjunto."
        ) from e


def manejo_credenciales(email: str):
    """Función que recibe credenciales para que sean cargadas."""

    from services.token_service import cargar_credenciales

    creds = cargar_credenciales(email=email)
    if not creds:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    return creds
