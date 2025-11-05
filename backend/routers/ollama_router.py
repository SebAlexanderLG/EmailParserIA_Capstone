from fastapi import APIRouter, HTTPException, Request
from fastapi import Body
from services.ollama_service import probar_conexion_ollama, generar_respuesta_ollama
from services.gmail_service import correo_completo

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
    """Endpoint que recibe cuerpo del correo y genera una respuesta IA"""
    email = request.cookies.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="No autenticado")

    mensaje_id = body.get("mensaje_id")
    prompt_key = body.get("prompt_key", "resumen_correo")

    if not mensaje_id:
        raise HTTPException(status_code=400, detail="Falta mensaje_id")

    # Traer cuerpo del correo (usar body_text)
    correo = correo_completo(email=email, mensaje_id=mensaje_id)
    cuerpo_correo = correo.get("body_text", "")

    if not cuerpo_correo:
        raise HTTPException(
            status_code=400, detail="El correo no tiene contenido de texto"
        )

    # Generar respuesta con Ollama
    try:
        respuesta_ia = generar_respuesta_ollama(prompt_key, cuerpo_correo)
    except Exception as e:
        raise HTTPException(status_code=500) from e

    return {"respuesta": respuesta_ia}
