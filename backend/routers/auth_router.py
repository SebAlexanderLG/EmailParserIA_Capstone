from fastapi import APIRouter, Request
from googleapiclient.discovery import build
from fastapi.responses import RedirectResponse, JSONResponse
from services.auth_service import autorizacion_gmail, auth_callback
from services.token_service import cargar_credenciales

router = APIRouter()


@router.get("/")
def inicio(email: str | None = None):
    """Si el usuario ya tiene token valido, se usa. Si no, redirige a autorización"""
    creds = None
    if email:
        creds = cargar_credenciales(email=email)

    if creds:
        service = build("gmail", "v1", credentials=creds)
        profile = service.users().getProfile(userId="me").execute()
        return JSONResponse(
            {"mensaje": "Ya tienes credenciales activas", "perfil": profile}
        )
    else:
        authorization_url = autorizacion_gmail()
        return RedirectResponse(url=authorization_url)


@router.get("/auth/callback")
def callback(request: Request):
    return auth_callback(request)
