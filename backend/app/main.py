from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import origins
from routers import auth_router, gmail_router, test_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router.router)
app.include_router(gmail_router.router)
app.include_router(test_router.router)
