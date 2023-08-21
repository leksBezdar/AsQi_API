from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import router as anime_router
from src.auth.routers import router as auth_router

app = FastAPI(
    title='AsQi'
)

app.include_router(anime_router, prefix="/animes", tags=["animes"])
app.include_router(auth_router, prefix="/registration", tags=["registration"])


origins = [
    "http://localhost",
    "http://localhost:5173",  # Пример для разработки на localhost
    "https://anime-blush.vercel.app/",    # Пример для реального домена (* ЗАМЕНИТЬ НА НАСТОЯЩИЙ)
]

# Добавление middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

