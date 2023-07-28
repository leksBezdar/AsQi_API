from fastapi import FastAPI
from app.api.anime import app as anime_app

app = FastAPI(
    title='AsQi'
)

app.include_router(anime_app, prefix="/animes", tags=["animes"])
