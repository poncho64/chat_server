from fastapi import FastAPI
from db import init_db
from auth import router as auth_router
from chat import router as chat_router

app = FastAPI()

init_db()

app.include_router(auth_router)
app.include_router(chat_router)
