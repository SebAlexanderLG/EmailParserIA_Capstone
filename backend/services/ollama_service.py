import requests
from datetime import datetime, timezone
from core.config import PROMPT, TIMEOUT, OLLAMA_URL, OLLAMA_URL_TEST
from sqlalchemy.orm import Session
from models.prompt import Prompt
from models.usuario import Usuario


def probar_conexion_ollama():
    """Verifica que el servidor de Ollama esté corriendo."""
    try:
        response = requests.get(OLLAMA_URL_TEST, timeout=10)
        if response.status_code == 200:
            modelos = [m["name"] for m in response.json().get("models", [])]
            return {"ok": True, "modelos_disponibles": modelos}
        else:
            return {
                "ok": False,
                "error": f"Ollama respondió con {response.status_code}",
            }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def generar_respuesta_ollama(prompt_usuario: str, cuerpo_correo: str):
    """Genera una respuesta IA usando el prompt libre definido por el usuario."""
    if not prompt_usuario:
        prompt_usuario = (
            "Redacta una respuesta profesional y cordial al siguiente correo:"
        )

    prompt_final = f"{prompt_usuario}\n\nContenido del correo:\n{cuerpo_correo}"

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": "llama3", "prompt": prompt_final, "stream": False},
            timeout=TIMEOUT,
        )
    except Exception as e:
        raise Exception(f"No se pudo conectar con Ollama: {e}")

    if response.status_code != 200:
        raise Exception(f"Error en Ollama: {response.text}")

    return response.json().get("response", "")


def guardar_prompt_usuario(email_cookie: str, contexto: str, db: Session):
    """Crea o actualiza el prompt personalizado del usuario."""
    if not contexto or len(contexto.strip()) < 10:
        raise ValueError("El contexto del prompt es demasiado corto.")

    usuario = db.query(Usuario).filter(Usuario.email == email_cookie).first()
    if not usuario:
        raise ValueError("Usuario no encontrado en la base de datos.")

    prompt_existente = db.query(Prompt).filter(Prompt.usuario_id == usuario.id).first()

    if prompt_existente:
        prompt_existente.contexto = contexto
        prompt_existente.fecha_creacion = datetime.now(timezone.utc)
        print(f"[INFO] Prompt actualizado para {email_cookie}")
    else:
        nuevo_prompt = Prompt(
            contexto=contexto,
            usuario_id=usuario.id,
            fecha_creacion=datetime.now(timezone.utc),
        )
        db.add(nuevo_prompt)
        print(f"[INFO] Prompt creado para {email_cookie}")

    db.commit()
