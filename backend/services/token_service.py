from datetime import datetime
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from utils.encriptacion_token import encrypt_token, decrypt_token
from google.auth.transport.requests import Request as GoogleRequest
from app.database import SessionLocal
from models import Usuario, GmailToken


from core.config import SCOPES


def guardar_token_db(tokens: dict) -> dict:
    """Guarda o actualiza tokens de Gmail en la base de datos (ENCRIPTADOS)."""

    db = SessionLocal()
    try:
        # Obtener correo del usuario usando access_token temporal
        creds = Credentials(
            token=tokens["access_token"],
            refresh_token=tokens.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            scopes=SCOPES,
        )

        service = build("gmail", "v1", credentials=creds)
        profile = service.users().getProfile(userId="me").execute()
        email = profile["emailAddress"]
        nombre_usuario = email.split("@")[0]

        access_enc = encrypt_token(tokens["access_token"])
        refresh_raw = tokens.get("refresh_token")
        refresh_enc = encrypt_token(refresh_raw) if refresh_raw else None

        # Buscar o crear usuario
        usuario = db.query(Usuario).filter_by(email=email).first()

        if not usuario:
            usuario = Usuario(
                nombre_usuario=nombre_usuario,
                email=email,
                oauth_access_token=access_enc,
                oauth_refresh_token=refresh_enc,
                ultima_sesion=datetime.now(),
            )
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
        else:
            usuario.oauth_access_token = access_enc
            usuario.oauth_refresh_token = refresh_enc
            usuario.ultima_sesion = datetime.now()
            db.commit()
            db.refresh(usuario)

        # Guardar token
        gmail_token = db.query(GmailToken).filter_by(usuario_id=usuario.id).first()

        if not gmail_token:
            gmail_token = GmailToken(
                usuario_id=usuario.id,
                access_token=access_enc,
                refresh_token=refresh_enc,
                token_type=tokens.get("token_type", "Bearer"),
                scope=json.dumps(tokens.get("scope", [])),
                expires_in=tokens.get("expires_in"),
                refresh_token_expires_in=tokens.get("refresh_token_expires_in"),
                expires_at=tokens["expires_at"],
                fecha_creacion=datetime.now(),
                fecha_actualizacion=datetime.now(),
            )
            db.add(gmail_token)
        else:
            gmail_token.access_token = access_enc
            gmail_token.refresh_token = refresh_enc
            gmail_token.token_type = tokens.get("token_type", "Bearer")
            gmail_token.scope = json.dumps(tokens.get("scope", []))
            gmail_token.expires_in = tokens.get("expires_in")
            gmail_token.refresh_token_expires_in = tokens.get(
                "refresh_token_expires_in"
            )
            gmail_token.expires_at = tokens["expires_at"]
            gmail_token.fecha_actualizacion = datetime.now()

        db.commit()
        db.refresh(gmail_token)

        return {
            "mensaje": "autorización exitosa",
            "usuario": {"id": usuario.id, "email": usuario.email},
            "token": {
                "id": gmail_token.id,
                "access_token": gmail_token.access_token,
            },
        }

    finally:
        db.close()


def cargar_credenciales(email: str | None = None) -> Credentials | None:
    """Carga credenciales desde la DB (DESENCRIPTADAS) y las refresca si es necesario."""
    db = SessionLocal()
    try:
        # Buscar token por email o tomar el primero
        if email:
            gmail_token = (
                db.query(GmailToken)
                .join(GmailToken.usuario)
                .filter(GmailToken.usuario.has(email=email))
                .first()
            )
        else:
            gmail_token = db.query(GmailToken).first()

        if not gmail_token:
            return None

        # DESENCRIPTAR LOS TOKENS DE LA BD
        access_token = decrypt_token(gmail_token.access_token)
        refresh_token = (
            decrypt_token(gmail_token.refresh_token)
            if gmail_token.refresh_token
            else None
        )

        # Construir credenciales reales
        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=SCOPES,
        )

        # REFRESCAR TOKENS SI EXPIRARON
        if creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())

            # Guardar nuevas credenciales — pero ENCRIPTADAS de nuevo 🔒
            gmail_token.access_token = encrypt_token(creds.token)

            if creds.refresh_token:
                gmail_token.refresh_token = encrypt_token(creds.refresh_token)

            gmail_token.expires_at = creds.expiry.timestamp() if creds.expiry else None
            gmail_token.fecha_actualizacion = datetime.now()
            db.commit()
            db.refresh(gmail_token)

        return creds

    finally:
        db.close()
