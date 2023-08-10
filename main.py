from fastapi import FastAPI
from api.routers import router as anime_router
from src.auth.routers import router as auth_router

app = FastAPI(
    title='AsQi'
)

app.include_router(anime_router, prefix="/animes", tags=["animes"])
app.include_router(auth_router, prefix="/registration", tags=["registration"])
