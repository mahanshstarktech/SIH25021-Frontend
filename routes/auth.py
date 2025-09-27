from fastapi import APIRouter, HTTPException, Form
import secrets

router = APIRouter()
USERS = {"admin": "password123"}
TOKENS = {}

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if username in USERS and USERS[username] == password:
        token = secrets.token_hex(16)
        TOKENS[token] = username
        return {"token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")
