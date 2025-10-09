from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.database import engine
from services.gmail_service import cargar_credenciales

router = APIRouter(tags=["Test"])


@router.post("/testbd")
def test_db():
    """Función para verificar conexión con BD"""
    try:
        with engine.connect():
            return {"mensaje": "¡Conexion exitosa"}
    except ImportError as e:
        return {"error": f"conexion fallida: {str(e)}"}


@router.get("/test_credenciales")
def test_credenciales(request: Request):
    """Función que verifica que hay una cookie"""
    # Tomamos el email de la cookie
    email = request.cookies.get("email")
    if not email:
        return JSONResponse({"error": "No hay cookie de email"}, status_code=400)

    # Cargamos las credenciales
    creds = cargar_credenciales(email=email)
    if not creds:
        return JSONResponse(
            {"error": "No se encontraron credenciales para este email"}, status_code=404
        )

    # Revisamos el estado de las credenciales
    return JSONResponse(
        {
            "email": email,
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "valid": creds.valid,
            "expired": creds.expired,
        }
    )
