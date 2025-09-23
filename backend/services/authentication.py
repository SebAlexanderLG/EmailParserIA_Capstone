import json
from googleapiclient.discovery import build
import google_auth_oauthlib.flow
from fastapi.responses import JSONResponse
from fastapi import Request
from google.oauth2.credentials import Credentials
from core.config import SCOPES, CLIENT_SECRETS_FILE
from app.database import SessionLocal
from models import Usuario, GmailToken
from datetime import datetime


def auth_load() -> dict:
    """Función para cargar la configuración del cliente desde el archivo JSON."""
    with open(CLIENT_SECRETS_FILE, encoding="utf-8") as f:
        return json.load(f)


def autorizacion_gmail() -> str:
    flow = google_auth_oauthlib.flow.Flow.from_client_config(auth_load(), scopes=SCOPES)
    # Cambiar URI de redirección a localhost para desarrollo local
    flow.redirect_uri = "http://localhost:8000/auth/callback"
    # Cambiar URI de redirección a la URL de Template de React o Django
    # flow.redirect_uri =

    authorization_url, state = flow.authorization_url(
        prompt="consent", access_type="offline", include_granted_scopes="true"
    )
    print("Por favor, ve a este enlace: {}".format(authorization_url))

    return authorization_url


def auth_callback(request: Request) -> JSONResponse:
    code: str | None = request.query_params.get("code")
    if not code:
        return JSONResponse(
            content={"error": "No se recibio ningún codigo de autorización"},
            status_code=400,
        )

    flow = google_auth_oauthlib.flow.Flow.from_client_config(auth_load(), scopes=SCOPES)
    flow.redirect_uri = "http://localhost:8000/auth/callback"
    tokens = flow.fetch_token(code=code)

    # Guardar token en archivo local
    with open("token.json", "w", encoding="utf8") as token_file:
        json.dump(tokens, token_file)

    # Crear objeto Credentials
    creds = Credentials(
        token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )

    # Obtener correo del usuario
    service = build("gmail", "v1", credentials=creds)
    profile = service.users().getProfile(userId="me").execute()
    email = profile["emailAddress"]
    nombre_usuario = email.split("@")[0]

    db = SessionLocal()

    try:
        usuario = db.query(Usuario).filter_by(email=email).first()
        if not usuario:
            usuario = Usuario(
                nombre_usuario=nombre_usuario,
                email=email,
                oauth_access_token=tokens["access_token"],
                oauth_refresh_token=tokens.get("refresh_token"),
                ultima_sesion=datetime.now(),
            )
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
        else:
            usuario.oauth_access_token = tokens["access_token"]
            usuario.oauth_refresh_token = tokens.get("refresh_token")
            usuario.ultima_sesion = datetime.now()
            db.commit()
            db.refresh(usuario)

        gmail_token = db.query(GmailToken).filter_by(usuario_id=usuario.id).first()
        if not gmail_token:
            gmail_token = GmailToken(
                usuario_id=usuario.id,
                access_token=tokens["access_token"],
                refresh_token=tokens.get("refresh_token"),
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
            gmail_token.access_token = tokens["access_token"]
            gmail_token.refresh_token = tokens.get("refresh_token")
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

        response = {
            "mensaje": "autorización exitosa",
            "usuario": {"id": usuario.id, "email": usuario.email},
            "token": {
                "id": gmail_token.id,
                "access_token": gmail_token.access_token,
            },
        }

    finally:
        db.close()

    return JSONResponse(content=response)
