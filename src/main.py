from fastapi import FastAPI
from .api import anime as anime_router
from .registration import main as registration_router

app = FastAPI(
    title='AsQi'
)

app.include_router(anime_router.router, prefix="/anime_api")

app.include_router(registration_router, prefix="/registration_api")
