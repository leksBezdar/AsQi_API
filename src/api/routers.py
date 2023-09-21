from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .models import Title

from . import schemas, exceptions
from ..database import get_async_session

from .service import DatabaseManager

router = APIRouter()


@router.post("/create_title/", response_model=schemas.TitleCreateDB)
async def create_title(
    title_data: schemas.TitleCreate,
    db: AsyncSession = Depends(get_async_session),
):
    
    db_manager = DatabaseManager(db)
    title_crud = db_manager.title_crud
    
    return await title_crud.create_title(title=title_data)


@router.post("/create_episode", response_model=schemas.EpisodeCreate)
async def create_episode(
    episode_data: schemas.EpisodeCreate,
    db: AsyncSession = Depends(get_async_session),
):
    
    db_manager = DatabaseManager(db)
    episode_crud = db_manager.episode_crud
    
    return await episode_crud.create_episode(episode=episode_data)


@router.get("/get_title", response_model=None)
async def get_title(
    db: AsyncSession = Depends(get_async_session),
    title_name: str = None,
    title_id: str = None):
    
    db_manager = DatabaseManager(db)
    title_crud = db_manager.title_crud
    
    title = await title_crud.get_existing_title(title_id=title_id, name=title_name)
    
    return title or {"Message": "No Title Found"}
    

@router.get("/titles/")
async def get_all_titles(
    db: AsyncSession = Depends(get_async_session),
    offset: int = 0,
    limit: int = 10):
    
    db_manager = DatabaseManager(db)
    title_crud = db_manager.title_crud
    
    titles = await title_crud.get_all_titles(offset=offset, limit=limit)
    
    return titles or {"Message": "No Titles Found"}


@router.get("/get_all_episodes")
async def get_all_episodes(
    title_id: str,
    offset: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session)):
    
    db_manager = DatabaseManager(db)
    episode_crud = db_manager.episode_crud
    
    episodes = await episode_crud.get_all_episodes(offset=offset, limit=limit, title_id=title_id) 
    
    return episodes or {"Message": "No Episodes Found"}


@router.get("/get_episode", response_model=None)
async def get_episode(
    episode_number: int,
    db: AsyncSession = Depends(get_async_session),
    title_id: str = None,
):
    
    db_manager = DatabaseManager(db)
    episode_crud = db_manager.episode_crud
    
    episode = await episode_crud.get_existing_episode(
        title_id = title_id,
        episode_number=episode_number
        )
    
    return episode or {"Message": "No Episode Found"}


@router.delete("/delete_title", response_model=None)
async def delete_title(
    db: AsyncSession = Depends(get_async_session),
    title_id: str = None,
    title_name: str = None,
):
    
    db_manager = DatabaseManager(db)
    title_crud = db_manager.title_crud
    
    return await title_crud.delete_title(title_id=title_id, title_name=title_name)


@router.delete("/delete_episode", response_model=None)
async def delete_episode(
    db: AsyncSession = Depends(get_async_session),
    title_id: str = None,
    title_name: str = None,
    episode_number: int = None,
    episode_title: str = None,
):
    
    db_manager = DatabaseManager(db)
    episode_crud = db_manager.episode_crud
    
    return await episode_crud.delete_episode(
        title_id=title_id,
        title_name=title_name,
        episode_number=episode_number,
        episode_title=episode_title
        )