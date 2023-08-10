from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import anime as anime_router
from .auth import routers as auth_router

app = FastAPI(
    title='AsQi'
)

app.include_router(anime_router.router, prefix="/anime_api")

app.include_router(auth_router, prefix="/registration_api")


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