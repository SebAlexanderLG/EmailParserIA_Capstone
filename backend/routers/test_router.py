from fastapi import APIRouter
from app.database import engine

router = APIRouter()


@router.post("/testbd")
def test_db():
    try:
        with engine.connect() as connection:
            return {"mensaje": "¡Conexion exitosa"}
    except Exception as e:
        return {"error": f"conexion fallida: {str(e)}"}
