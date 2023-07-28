# app/main.py
from fastapi import FastAPI
from app.api import anime

app = FastAPI(
    title='AsQi'
)

app.include_router(anime.router, prefix="/api")
