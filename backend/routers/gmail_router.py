from fastapi import APIRouter, Request, HTTPException
from fastapi import Body
from fastapi.responses import JSONResponse
from utils.correos import descargar_adjunto_gmail
from services.gmail_service import (
    obtener_nombre_real,
    obtener_correos_preview,
    correo_completo,
    marcar_correo_leido,
    eliminar_correo,
)

router = APIRouter(prefix="/gmail", tags=["Gmail"])


@router.get("/perfil_gmail")
def perfil_gmail(request: Request):
    """Endpoint que trae el nombre real del usuario Gmail"""
    print("Todas las cookies:", request.cookies)
    email = request.cookies.get("email")
    print("Email autenticado:", email)
    if not email:
        raise HTTPException(status_code=401, detail="No autenticado")
    return obtener_nombre_real(email)


@router.post("/correosPreview")
def correos_preview(request: Request, body: dict = Body(...)):
    """Endpoint que trae una cantidad de correos en vista previa"""
    email = request.cookies.get("email")
    print("Email autenticado:", email)
    if not email:
        raise HTTPException(status_code=401, detail="No autenticado")
    limit = body.get("limit", 20)
    formato = body.get("formato", "metadata")
    return obtener_correos_preview(email, limit, formato)


@router.get("/correos")
def correos(mensaje_id: str, request: Request):
    """Endpoint que trae correo completo"""
    # Leer email desde la cookie HttpOnly enviada en el request
    email = request.cookies.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="No se encontró el email")
    return correo_completo(email=email, mensaje_id=mensaje_id)


@router.get("/descargar_adjunto")
def descargar_adjunto_correo(
    request: Request, mensaje_id: str, attachment_id: str, filename: str = None
):
    """Endpoint que permite descargar archivos adjuntos de un correo"""
    email = request.cookies.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="No autenticado")

    return descargar_adjunto_gmail(
        email=email,
        mensaje_id=mensaje_id,
        attachment_id=attachment_id,
        filename=filename,
    )


@router.post("/marcar_leido")
def marcar_leido(request: Request, body: dict = Body(...)):
    """Endpoint que permite marcar un correo como leido"""
    email = request.cookies.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="No autenticado")
    mensaje_id = body.get("mensaje_id")
    if not mensaje_id:
        raise HTTPException(
            status_code=400, detail="Faltan parametros para la solicitud."
        )
    return marcar_correo_leido(email=email, mensaje_id=mensaje_id)


@router.delete("/eliminar_correo")
def eliminar_correo_gmail(request: Request, body: dict = Body(...)):
    email = request.cookies.get("email")
    if not email:
        raise HTTPException(status_code=4001, detail="No autenticado")
    mensaje_id = body.get("mensaje_id")
    if not mensaje_id:
        raise HTTPException(
            status_code=400, detail="Faltan parametros para la solicitud."
        )
    return eliminar_correo(email=email, mensaje_id=mensaje_id)


@router.post("/logout")
def logout():
    """Endpoint para cerrar sesión"""
    response = JSONResponse({"ok": True})
    response.delete_cookie("email", path="/")
    return response
