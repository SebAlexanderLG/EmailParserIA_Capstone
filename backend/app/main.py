from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from services.authentication import autorizacion_gmail

app = FastAPI()


@app.get("/")
def autenticacion():
    authorization_url = autorizacion_gmail()
    return RedirectResponse(url=authorization_url)
