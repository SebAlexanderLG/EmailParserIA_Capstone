from bs4 import BeautifulSoup
from fastapi import HTTPException
from email.utils import parsedate_to_datetime
from googleapiclient.discovery import build
from fastapi.responses import RedirectResponse
from utils import (
    extraer_encabezados,
    extraer_asunto,
    extraer_remitente,
    procesar_payload,
    extraer_fecha_correo,
)
from .token_service import cargar_credenciales


def obtener_perfil(email: str):
    """Función que obtiene el perfil del usuario Gmail"""
    creds = cargar_credenciales(email=email)
    if not creds:
        return RedirectResponse(url="/")

    service = build("gmail", "v1", credentials=creds)
    profile = service.users().getProfile(userId="me").execute()
    nombre_usuario = email.split("@")[0]
    return {"profile": profile, "nombre_usuario": nombre_usuario}


def obtener_nombre_real(email: str):
    """Función que obtiene el nombre real del usuario Gmail"""
    creds = cargar_credenciales(email=email)
    if not creds:
        return {"error": "No hay credenciales"}

    # Construir servicio de People API
    service = build("people", "v1", credentials=creds)

    profile = (
        service.people().get(resourceName="people/me", personFields="names").execute()
    )

    nombre_real = profile.get("names", [{}])[0].get("displayName", "")
    return {"nombre_real": nombre_real}


def obtener_correos_preview(
    email: str,
    limit: int = 20,
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

            if "date" in correo_simplificado and correo_simplificado["date"]:
                try:
                    dt = parsedate_to_datetime(correo_simplificado["date"])
                    correo_simplificado["date"] = dt.strftime("%d/%m/%Y %H:%M")
                except ImportError:
                    pass
            if "from" in correo_simplificado and "<" in correo_simplificado["from"]:
                nombre, mail = correo_simplificado["from"].split("<")
                correo_simplificado["from_name"] = nombre.strip()
            else:
                correo_simplificado["from_name"] = correo_simplificado.get("from", "")
            correo_simplificado["snippet"] = correo.get("snippet", "")
            correo_simplificado["id"] = msg["id"]

            correos.append(correo_simplificado)
        else:
            correos.append(correo)
    return correos


def limpiar_html(html: str) -> str:
    """Devuelve solo el contenido visible del body del HTML"""
    soup = BeautifulSoup(html, "html.parser")

    # eliminar head
    if soup.head:
        soup.head.decompose()

    # eliminar estilos y scripts
    for tag in soup(["style", "script"]):
        tag.decompose()

    # eliminar comentarios
    for comment in soup.find_all(
        string=lambda text: isinstance(text, type(soup.Comment))
    ):
        comment.extract()

    # devolver solo el body si existe
    if soup.body:
        return str(soup.body)
    return str(soup)


def correo_completo(email: str, mensaje_id: str) -> dict:
    """Trae el correo completo según su ID y limpia HTML pesado"""
    creds = cargar_credenciales(email=email)
    if not creds:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    service = build("gmail", "v1", credentials=creds)
    correo = (
        service.users()
        .messages()
        .get(userId="me", id=mensaje_id, format="full")
        .execute()
    )

    payload = correo.get("payload", {})
    headers = extraer_encabezados(payload)
    asunto = extraer_asunto(headers)
    remitente = extraer_remitente(headers)
    fecha = extraer_fecha_correo(headers)

    body_text, body_html, attachments = procesar_payload(payload, service, mensaje_id)

    # Si no hay texto plano, crearlo a partir del HTML
    if not body_text and body_html:
        body_text = BeautifulSoup(body_html, "html.parser").get_text("\n", strip=True)

    # Limpiar HTML antes de enviarlo
    if body_html:
        body_html = limpiar_html(body_html)

    return {
        "from": remitente,
        "subject": asunto,
        "date": fecha,
        "body_text": body_text,
        "body_html": body_html,
        "attachments": attachments,
    }
