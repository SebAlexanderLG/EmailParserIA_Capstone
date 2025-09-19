"""Permisos para gmail API"""

SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.addons.current.message.action",
    "https://www.googleapis.com/auth/gmail.addons.current.message.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]
CLIENT_SECRETS_FILE = "credentials.json"

DATABASE_URL_CONECTION = "postgresql://postgres:1234@localhost:5432/parser"
