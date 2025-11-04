SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.addons.current.message.action",
    "https://www.googleapis.com/auth/gmail.addons.current.message.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.modify",
]
CLIENT_SECRETS_FILE = "credentials.json"

DATABASE_URL_CONECTION = "postgresql://postgres:1234@localhost:5432/parser"

origins = ["http://localhost:5173"]

OLLAMA_URL_TEST = "http://localhost:11434/api/tags"
OLLAMA_URL = "http://localhost:11434/api/generate"
TIMEOUT = 120
PROMPT = {
    "resumen_correo": "Resume este correo en 3 lineas",
    "respuesta_ia": "Analiza el correo y genera una respuesta logica y coherente en base al mensaje recibido y representando, en primera persona al docente a quien recibe el correo.",
}
