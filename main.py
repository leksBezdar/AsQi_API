from fastapi import FastAPI
from src.api.anime import router

app = FastAPI(
    title='AsQi'
)

app.include_router(router, prefix="/animes", tags=["animes"])
