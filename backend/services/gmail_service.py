from googleapiclient.discovery import build
from .token_service import cargar_credenciales


def obtener_correos_preview(
    email: str,
    limit: int = 10,
    format_type: str = "metadata",
    headers: list | None = None,
) -> list:
    """Retorna un preview de cada correo (como la lista de gmail)."""
    if headers is None:
        headers = ["From", "Subject", "Date"]

    creds = cargar_credenciales(email=email)
    if not creds:
        return []

    service = build("gmail", "v1", credentials=creds)

    # Lista IDs de correos
    results = (
        service.users()
        .messages()
        .list(
            userId="me",
            labelIds=["INBOX"],
            q="is:unread -category:promotions -category:social",
            maxResults=limit,
        )
        .execute()
    )
    messages = results.get("messages", [])

    correos = []
    seen_ids = set()
    for msg in messages:
        if msg["id"] in seen_ids:
            continue
        seen_ids.add(msg["id"])

        correo = (
            service.users()
            .messages()
            .get(userId="me", id=msg["id"], format=format_type, metadataHeaders=headers)
            .execute()
        )

        if format_type == "metadata":
            correo_simplificado = {}

            for h in headers:
                valor = next(
                    (
                        item["value"]
                        for item in correo["payload"]["headers"]
                        if item["name"] == h
                    ),
                    "",
                )
                correo_simplificado[h.lower()] = valor
            correo_simplificado["snippet"] = correo.get("snippet", "")

            correos.append(correo_simplificado)
        else:
            correos.append(correo)

    return correos
