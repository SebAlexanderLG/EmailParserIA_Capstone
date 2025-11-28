import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener clave de encriptación desde .env
FERNET_KEY = os.getenv("ENCRYPT_KEY")

if not FERNET_KEY:
    raise ValueError(
        "ERROR: Falta ENCRYPT_KEY en .env. Genera una con Fernet.generate_key()."
    )

# Inicializar Fernet
fernet = Fernet(FERNET_KEY.encode())


def encrypt_token(token: str) -> str:
    """Encripta un token OAuth para guardarlo en BD."""
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(token: str) -> str:
    """Desencripta un token guardado."""
    return fernet.decrypt(token.encode()).decode()
