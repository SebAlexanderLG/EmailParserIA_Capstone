from email.utils import parsedate_to_datetime
from email.mime.text import MIMEText
from datetime import datetime
import re
import base64
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup
from fastapi.responses import RedirectResponse
from googleapiclient.discovery import build
from models.email import Email
from models.remitente import Remitente
from models.usuario import Usuario
from utils.correos import manejo_credenciales
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
    creds = manejo_credenciales(email)

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
    page_token: str | None = None,
) -> dict:
    """Retorna correos paginados usando Gmail API (nextPageToken real)."""

    if headers is None:
        headers = ["From", "Subject", "Date"]

    creds = manejo_credenciales(email)
    service = build("gmail", "v1", credentials=creds)

    params = {
        "userId": "me",
        "labelIds": ["INBOX"],
        "maxResults": limit,
    }

    # Si viene un token → pedir la página siguiente
    if page_token:
        params["pageToken"] = page_token

    # Ejecutar petición
    results = service.users().messages().list(**params).execute()

    messages = results.get("messages", [])
    next_page_token = results.get("nextPageToken")

    correos = []
    seen_ids = set()

    for msg in messages:
        if msg["id"] in seen_ids:
            continue
        seen_ids.add(msg["id"])

        correo = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=msg["id"],
                format=format_type,
                metadataHeaders=headers,
            )
            .execute()
        )

        correo_simplificado = {}

        for h in headers:
            valor = next(
                (
                    item["value"]
                    for item in correo.get("payload", {}).get("headers", [])
                    if item["name"] == h
                ),
                "",
            )
            correo_simplificado[h.lower()] = valor

        # Procesar fecha
        if correo_simplificado.get("date"):
            try:
                dt = parsedate_to_datetime(correo_simplificado["date"])
                correo_simplificado["date"] = dt.strftime("%d/%m/%Y %H:%M")
            except Exception as e:
                pass

        # From → name
        from_value = correo_simplificado.get("from", "")
        if "<" in from_value:
            nombre, _ = from_value.split("<")
            correo_simplificado["from_name"] = nombre.strip()
        else:
            correo_simplificado["from_name"] = from_value

        correo_simplificado["snippet"] = correo.get("snippet", "")
        correo_simplificado["id"] = msg["id"]

        labels = correo.get("labelIds", [])
        correo_simplificado["leido"] = "UNREAD" not in labels

        correos.append(correo_simplificado)

    return {"correos": correos, "nextPageToken": next_page_token}


def registrar_correo_en_bd(
    email_cookie: str, correo: dict, mensaje_id: str, db: Session
):
    """Registra un correo en la BD si no existe y agrega a remitente si es necesario."""

    # Evita duplicados en consulta
    if db.query(Email).filter(Email.email_id == mensaje_id).first():
        return

    remitente_str = correo.get("from", "") or correo.get("from_name", "")
    asunto = correo.get("subject", "") or correo.get("asunto", "")
    cuerpo_snippet = correo.get("snippet", "")[:500]
    fecha_hora = datetime.now()

    # Buscar destinatario (usuario autenticado)
    usuario_dest = db.query(Usuario).filter(Usuario.email == email_cookie).first()
    if not usuario_dest:
        raise ValueError("Usuario autenticado no encontrado en la base de datos.")

    # Buscar si hay un remitente, si no, lo agrega a la BD
    remitente_db = (
        db.query(Remitente)
        .filter(
            Remitente.nombre_correo == remitente_str,
            Remitente.usuario_id == usuario_dest.id,
        )
        .first()
    )
    if not remitente_db:
        remitente_db = Remitente(
            usuario_id=usuario_dest.id,
            nombre_correo=remitente_str,
            nombre_remitente=None,
        )
        db.add(remitente_db)
        db.commit()
        db.refresh(remitente_db)

    # Inserta campos del correo
    nuevo_email = Email(
        fecha_hora_correo=fecha_hora,
        email_id=mensaje_id,
        remitente_id=remitente_db.id,
        destinatario_id=usuario_dest.id,
        asunto=asunto,
        cuerpo_snippet=cuerpo_snippet,
    )

    db.add(nuevo_email)
    db.commit()
    db.refresh(nuevo_email)

    print(f"[INFO] Correo {mensaje_id} registrado en la BD.")


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
    creds = manejo_credenciales(email)
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

    # Limpia HTML antes de enviarlo
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


def marcar_correo_leido(email: str, mensaje_id: str):
    """Función que marca correos como leido"""
    creds = manejo_credenciales(email)
    service = build("gmail", "v1", credentials=creds)

    service.users().messages().modify(
        userId="me", id=mensaje_id, body={"removeLabelIds": ["UNREAD"]}
    ).execute()

    return {"ok": True, "mensaje_id": mensaje_id}


def marcar_correo_no_leido(email: str, mensaje_id: str):
    """Función que marca correos como leido"""
    creds = manejo_credenciales(email)
    service = build("gmail", "v1", credentials=creds)

    service.users().messages().modify(
        userId="me", id=mensaje_id, body={"addLabelIds": ["UNREAD"]}
    ).execute()

    return {"ok": True, "mensaje_id": mensaje_id}


def eliminar_correo(email: str, mensaje_id: str):
    """Función que permite eliminar un correo de la bandeja"""
    creds = manejo_credenciales(email)
    service = build("gmail", "v1", credentials=creds)
    service.users().messages().trash(userId="me", id=mensaje_id).execute()

    return {"ok": True, "mensaje_id": mensaje_id}


def enviar_respuesta_correo(email_usuario: str, mensaje_id: str, cuerpo_respuesta: str):
    """Envía una respuesta al correo original usando Gmail API"""
    try:
        creds = manejo_credenciales(email_usuario)
        service = build("gmail", "v1", credentials=creds)

        # Obtiene el correo original (solo metadata)
        mensaje_original = (
            service.users()
            .messages()
            .get(userId="me", id=mensaje_id, format="metadata")
            .execute()
        )

        headers = mensaje_original.get("payload", {}).get("headers", [])
        subject = next(
            (h["value"] for h in headers if h["name"] == "Subject"), "(sin asunto)"
        )
        remitente_raw = next((h["value"] for h in headers if h["name"] == "From"), None)
        message_id_header = next(
            (h["value"] for h in headers if h["name"].lower() == "message-id"), None
        )

        if not remitente_raw:
            raise ValueError("No se encontró el remitente del correo original.")

        # Limpia y extrae solo el correo electrónico
        match = re.search(r"<(.+?)>", remitente_raw)
        remitente = match.group(1) if match else remitente_raw.strip()

        # Crear mensaje MIME (UTF-8)
        mensaje = MIMEText(cuerpo_respuesta, "plain", "utf-8")
        mensaje["to"] = remitente
        mensaje["subject"] = f"Re: {subject}"

        # Mantener el hilo original (si tiene Message-ID)
        if message_id_header:
            mensaje["In-Reply-To"] = message_id_header
            mensaje["References"] = message_id_header

        # Codifica mensaje (Base64 URL-safe)
        raw = base64.urlsafe_b64encode(mensaje.as_bytes()).decode("utf-8")

        # Envia el correo
        service.users().messages().send(userId="me", body={"raw": raw}).execute()

        print(f"[INFO] ✅ Respuesta enviada correctamente a {remitente}")
        return True

    except Exception as e:
        print(f"[ERROR] Fallo al enviar correo: {e}")
        raise ValueError("No se pudo enviar el correo.") from e
