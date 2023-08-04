from fastapi import FastAPI
from .api import anime

app = FastAPI(
    title='AsQi'
)

app.include_router(anime.router, prefix="/api")
