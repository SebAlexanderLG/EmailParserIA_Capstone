from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
from fastapi import Body
from fastapi.responses import JSONResponse
from models.email import Email
from app.database import SessionLocal
from utils.correos import descargar_adjunto_gmail
from services.gmail_service import (
    obtener_nombre_real,
    obtener_correos_preview,
    correo_completo,
    marcar_correo_leido,
    marcar_correo_no_leido,
    eliminar_correo,
    registrar_correo_en_bd,
    enviar_respuesta_correo,
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
    """Endpoint que trae correos en vista previa con paginación real."""

    email = request.cookies.get("email")
    print("Email autenticado:", email)

    if not email:
        raise HTTPException(status_code=401, detail="No autenticado")

    limit = body.get("limit", 20)
    formato = body.get("formato", "metadata")
    page_token = body.get("page_token")

    return obtener_correos_preview(
        email=email,
        limit=limit,
        format_type=formato,
        page_token=page_token,
    )


@router.get("/correos")
def correos(mensaje_id: str, request: Request):
    """Endpoint que trae correo completo + respuesta IA (si existe en BD)"""
    email = request.cookies.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="No se encontró el email")

    # Obtiene el correo desde Gmail API (from, subject, body, etc.)
    correo = correo_completo(email=email, mensaje_id=mensaje_id)

    db = SessionLocal()
    respuesta_ia = None
    fecha_envio_str = None

    try:
        # Registra en BD si no existe
        registrar_correo_en_bd(email, correo, mensaje_id, db)

        # Busca el registro del correo en la BD
        email_db = db.query(Email).filter(Email.email_id == mensaje_id).first()
        if email_db:
            respuesta_ia = email_db.respuesta_ia
            if email_db.fecha_envio:
                fecha_envio_str = email_db.fecha_envio.strftime("%Y-%m-%d %H:%M:%S")

        db.commit()
    except Exception as e:
        print(f"[WARN] No se pudo registrar/leer correo {mensaje_id}: {e}")
        db.rollback()
    finally:
        db.close()

    return {
        **correo,
        "respuesta_ia": respuesta_ia,
        "fecha_envio": fecha_envio_str,
    }


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
    email = request.cookies.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="No autenticado")

    mensaje_id = body.get("mensaje_id")
    return marcar_correo_leido(email, mensaje_id)


@router.post("/marcar_no_leido")
def marcar_no_leido(request: Request, body: dict = Body(...)):
    email = request.cookies.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="No autenticado")

    mensaje_id = body.get("mensaje_id")
    return marcar_correo_no_leido(email, mensaje_id)


@router.delete("/eliminar_correo")
def eliminar_correo_gmail(request: Request, body: dict = Body(...)):
    """Función que elimina correo de buzón"""
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


@router.post("/enviar_respuesta")
def enviar_respuesta(request: Request, body: dict = Body(...)):
    """Envía un correo de respuesta y guarda la fecha de envío + respuesta IA"""
    email_cookie = request.cookies.get("email")
    if not email_cookie:
        raise HTTPException(status_code=401, detail="No autenticado")

    mensaje_id = body.get("mensaje_id")
    respuesta_texto = body.get("respuesta_texto")

    if not mensaje_id or not respuesta_texto:
        raise HTTPException(
            status_code=400, detail="Faltan parámetros: mensaje_id o respuesta_texto."
        )

    db = SessionLocal()
    try:
        # Envia el mensaje del correo usando Gmail API
        enviar_respuesta_correo(email_cookie, mensaje_id, respuesta_texto)

        # Guarda mensaje en la BD
        email_db = db.query(Email).filter(Email.email_id == mensaje_id).first()
        if not email_db:
            raise HTTPException(status_code=404, detail="Correo no encontrado en BD")

        email_db.respuesta_ia = respuesta_texto
        email_db.fecha_envio = datetime.now()

        db.commit()

        return {
            "ok": True,
            "fecha_envio": email_db.fecha_envio.strftime("%Y-%m-%d %H:%M:%S"),
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500) from e
    finally:
        db.close()
