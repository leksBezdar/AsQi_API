from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import crud
from ..db import schemas 
from ..database import get_async_session

router = APIRouter()


@router.post("/animes/", response_model=schemas.AnimeCreate)
async def create_anime_endpoint(
    anime_data: schemas.AnimeCreate,
    session: AsyncSession = Depends(get_async_session),
):
    anime = await crud.create_anime(session, anime_data)
    return anime

@router.get("/animes/{anime_id_or_title}", response_model=schemas.Anime)
async def read_anime_by_id_or_title(anime_id_or_title: str, db: AsyncSession = Depends(get_async_session)):
    try:
        anime_id = int(anime_id_or_title)
        return await crud.get_anime_by_id(db=db, anime_id=anime_id)
    except ValueError:
        return await crud.get_anime_by_id(db=db, title=anime_id_or_title)