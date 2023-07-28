from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import NoResultFound
from typing import List

from app.db import crud
from ..db import schemas 
from ..database import get_async_session

router = APIRouter()


@router.post("/animes/", response_model=schemas.AnimeCreate)
async def create_anime(
    anime_data: schemas.AnimeCreate,
    db: AsyncSession = Depends(get_async_session),
):
    if  await crud.read_anime_by_id(db=db, title=anime_data.title):
        raise HTTPException(status_code=409, detail='Title already exists or item conflict')
    return await crud.create_anime(db, anime_data)


@router.post("/animes/{anime_id}/episodes/", response_model=schemas.Episode)
async def create_anime_episode(
    anime_id: int,
    episode_data: schemas.EpisodeCreate,
    db: AsyncSession = Depends(get_async_session),
):
    anime = await crud.read_anime_by_id(db=db, anime_id=anime_id)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    return await crud.create_episode(db=db, anime_id=anime_id, episode=episode_data)


@router.get("/animes/{anime_id_or_title}", response_model=schemas.Anime)
async def read_anime_by_id_or_title(anime_id_or_title: str, db: AsyncSession = Depends(get_async_session)):
    try:
        anime_id = int(anime_id_or_title)
        return await crud.read_anime_by_id(db=db, anime_id=anime_id)
    except ValueError:
        return await crud.read_anime_by_id(db=db, title=anime_id_or_title)
    

@router.get("/animes/", response_model=List[schemas.Anime])
async def read_all_animes(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_async_session)):
    return await crud.read_all_animes(db=db, skip=skip, limit=limit)


@router.get("/animes/{anime_id}/episodes/", response_model=List[schemas.Episode])
async def read_anime_episodes(anime_id: int, db: AsyncSession = Depends(get_async_session)):
    anime = await crud.read_anime_by_id(db=db, anime_id=anime_id)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    
    return await crud.read_all_episodes_for_anime(db=db, anime_id=anime_id)