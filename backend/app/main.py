from fastapi import FastAPI
from routers import auth_router, gmail_router, test_router

app = FastAPI()

app.include_router(auth_router.router)
app.include_router(gmail_router.router)
app.include_router(test_router.router)
