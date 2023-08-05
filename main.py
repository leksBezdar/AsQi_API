from fastapi import FastAPI
from src.api.anime import router as anime_router
from src.registration.main import router as registration_router

app = FastAPI(
    title='AsQi'
)

app.include_router(anime_router, prefix="/animes", tags=["animes"])
app.include_router(registration_router, prefix="/registration", tags=["registration"])
