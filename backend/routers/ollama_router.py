from fastapi import APIRouter, HTTPException, Request
from fastapi import Body
from services.ollama_service import probar_conexion_ollama, generar_respuesta_ollama
from services.gmail_service import correo_completo
from fastapi import APIRouter, Request, HTTPException, Body
from app.database import SessionLocal
from services.ollama_service import guardar_prompt_usuario

router = APIRouter(prefix="/ollama", tags=["Ollama"])


@router.get("/test")
def test_ollama():
    """Verifica si Ollama está corriendo y devuelve los modelos disponibles"""
    resultado = probar_conexion_ollama()
    if not resultado["ok"]:
        raise HTTPException(status_code=500, detail=resultado["error"])
    return resultado


@router.post("/generar_respuesta_ia")
def generar_respuesta_ia(request: Request, body: dict = Body(...)):
    """Genera una respuesta IA a partir de un prompt personalizado."""
    email = request.cookies.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="No autenticado")

    mensaje_id = body.get("mensaje_id")
    prompt_usuario = body.get("prompt_key", "").strip()

    if not mensaje_id:
        raise HTTPException(status_code=400, detail="Falta mensaje_id")

    # 🔹 Traer cuerpo del correo
    correo = correo_completo(email=email, mensaje_id=mensaje_id)
    cuerpo_correo = correo.get("body_text", "") or correo.get("body_html", "")
    if not cuerpo_correo:
        raise HTTPException(
            status_code=400, detail="El correo no tiene contenido de texto"
        )

    # 🔹 Si el usuario no pasó prompt, usar uno por defecto
    if not prompt_usuario:
        prompt_usuario = (
            "Redacta una respuesta profesional y cordial al siguiente correo:"
        )

    try:
        respuesta_ia = generar_respuesta_ollama(prompt_usuario, cuerpo_correo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"respuesta": respuesta_ia}


@router.post("/guardar_prompt")
def guardar_prompt(request: Request, body: dict = Body(...)):
    """Guarda o actualiza el prompt personalizado del usuario."""
    email = request.cookies.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="No autenticado")

    contexto = body.get("contexto", "").strip()
    if not contexto:
        raise HTTPException(status_code=400, detail="El prompt no puede estar vacío")

    db = SessionLocal()
    try:
        guardar_prompt_usuario(email, contexto, db)
        return {"ok": True, "mensaje": "Prompt guardado correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
