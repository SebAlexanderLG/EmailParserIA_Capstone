from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from services.authentication import autorizacion_gmail, auth_callback
from app.database import engine

app = FastAPI()


@app.get("/")
def autenticacion():
    authorization_url = autorizacion_gmail()
    return RedirectResponse(url=authorization_url)


@app.get("/auth/callback")
def callback(request: Request):
    return auth_callback(request)


@app.get("/testbd")
def test_db():
    try:
        with engine.connect() as connection:
            return {"mensaje": "¡Conexion exitosa"}
    except Exception as e:
        return {"error": f"conexion fallida: {str(e)}"}
