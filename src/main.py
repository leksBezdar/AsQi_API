from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from src.api.routers import router as anime_router
from src.auth.routers import router as auth_router
from src.chat.routers import router as chat_router
from src.pages.routers import router as page_router

app = FastAPI(
    title='AsQi'
)

app.include_router(anime_router, tags=["titles"])
app.include_router(auth_router, tags=["registration"])
app.include_router(chat_router, tags=["chat"])
app.include_router(page_router, tags=["pages"])


origins = [
    "http://localhost",
    "http://localhost:5173",
    "https://anime-blush.vercel.app/",
]

# Добавление middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <a href="http://127.0.0.1:8000/docs"><h1>Documentation</h1></a><br>
    <a href="http://127.0.0.1:8000/redoc"><h1>ReDoc</h1></a>
    """