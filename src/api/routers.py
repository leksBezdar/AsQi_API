from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from . import schemas, exceptions, service 
from ..database import get_async_session

router = APIRouter()


@router.post("/animes/", response_model=schemas.AnimeBase)
async def create_anime(
    anime_data: schemas.AnimeBase,
    db: AsyncSession = Depends(get_async_session),
):
    
    if  await service.get_existing_anime(db=db, title=anime_data.title):
        raise exceptions.TitleAlreadyExists
    return await service.create_anime(db, anime_data)


@router.post("/animes/{anime_id}/episodes/", response_model=schemas.Episode)
async def create_anime_episode(
    episode_data: schemas.EpisodeBase,
    db: AsyncSession = Depends(get_async_session),
):
    anime = await service.read_anime_by_id_or_title(db=db, anime_id=episode_data.anime_id)
    
    if not anime:
        raise exceptions.TitleWasNotFound
    
    return await service.create_episode(db=db, anime_id=episode_data.anime_id, episode=episode_data)


@router.get("/animes/{anime_id_or_title}", response_model=schemas.Anime)
async def read_anime_by_id_or_title(anime_id_or_title: str, db: AsyncSession = Depends(get_async_session)):
    try:
        anime_id = int(anime_id_or_title)
        return await service.read_anime_by_id_or_title(db=db, anime_id=anime_id)
    except ValueError:
        return await service.read_anime_by_id_or_title(db=db, title=anime_id_or_title)
    

@router.get("/animes/", response_model=List[schemas.Anime])
async def read_all_animes(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_async_session)):
    return await service.read_all_animes(db=db, skip=skip, limit=limit)


@router.get("/animes/{anime_id}/episodes/", response_model=List[schemas.Episode])
async def read_anime_episodes(anime_id: int, db: AsyncSession = Depends(get_async_session)):
    anime = await service.read_anime_by_id_or_title(db=db, anime_id=anime_id)
    if not anime:
        raise exceptions.TitleWasNotFound
    
    return await service.read_all_episodes_for_anime(db=db, anime_id=anime_id)