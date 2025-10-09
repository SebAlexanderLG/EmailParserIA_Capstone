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

prompt = {
    "model": "llama3",
    "prompt": "Analiza el correo y dime de que trata",
}
