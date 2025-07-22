from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import sqlite3
import os
from db import DB_PATH, AVATAR_DIR, hash_password
from models import UserRegister, UserLogin, UserOut

router = APIRouter()

@router.post("/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    avatar: UploadFile = File(None)
):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    avatar_filename = None
    if avatar:
        ext = os.path.splitext(avatar.filename)[1] if avatar.filename else ''
        avatar_filename = f"{username}{ext}"
        avatar_path = os.path.join(AVATAR_DIR, avatar_filename)
        with open(avatar_path, "wb") as f:
            f.write(await avatar.read())
    c.execute(
        "INSERT INTO users (username, password_hash, avatar) VALUES (?, ?, ?)",
        (username, hash_password(password), avatar_filename)
    )
    conn.commit()
    conn.close()
    return {"msg": "Registro exitoso"}

@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password_hash, avatar FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if not row or row[0] != hash_password(password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {"msg": "Login exitoso", "avatar": row[1]}

@router.get("/avatar/{username}")
async def get_avatar(username: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT avatar FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        avatar_path = os.path.join(AVATAR_DIR, row[0])
        if os.path.exists(avatar_path):
            return FileResponse(avatar_path)
    raise HTTPException(status_code=404, detail="Avatar no encontrado")
