from fastapi import APIRouter, Request, HTTPException
from fastapi import Body
from fastapi.responses import JSONResponse
from services.gmail_service import (
    obtener_nombre_real,
    obtener_correos_preview,
    correo_completo,
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


@router.post("/logout")
def logout():
    """Endpoint para cerrar sesión"""
    response = JSONResponse({"ok": True})
    response.delete_cookie("email", path="/")
    return response


@router.get("/correos")
def correos(mensaje_id: str, request: Request):
    # Leer email desde la cookie HttpOnly enviada en el request
    email = request.cookies.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="No se encontró el email")
    return correo_completo(email=email, mensaje_id=mensaje_id)
