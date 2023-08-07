from fastapi import FastAPI
from .api import anime as anime_router
from .auth import routers as auth_router

app = FastAPI(
    title='AsQi'
)

app.include_router(anime_router.router, prefix="/anime_api")

app.include_router(auth_router, prefix="/registration_api")
