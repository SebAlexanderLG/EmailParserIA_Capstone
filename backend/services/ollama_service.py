import requests
from core.config import PROMPT, TIMEOUT, OLLAMA_URL, OLLAMA_URL_TEST


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


def generar_respuesta_ollama(prompt: str, cuerpo_correo: str):
    """Lee un prompt y genera una respuesta"""
    prompt_usuario = PROMPT.get(prompt)
    if not prompt_usuario:
        raise ValueError(f"No se encontro el prompt: {prompt}")

    prompt = f"{prompt_usuario}\n\nContenido del correo:\n{cuerpo_correo}"

    response = requests.post(
        OLLAMA_URL,
        json={"model": "llama3", "prompt": prompt, "stream": False},
        timeout=TIMEOUT,
    )

    if response.status_code != 200:
        raise ValueError(f"Error en Ollama: {response.text}")
    return response.json().get("response", "")
