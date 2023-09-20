from typing import List
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from sqlalchemy.future import select

from .models import Title, Episode
from .dao import TitleDAO, EpisodeDAO
from . import schemas, exceptions


class TitleCrud:
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_title(self, title: schemas.TitleCreate) -> Title:
        
        title_exist = await self.get_existing_title(name=title.name, trailer_link=title.trailer_link)
        
        if title_exist:
            raise exceptions.TitleAlreadyExists
        
        id = str(uuid4())
        
        db_title = await TitleDAO.add(
            self.db,
            schemas.TitleCreate(
            **title.model_dump(),
            id = id,
            )
        )

        self.db.add(db_title)
        await self.db.commit()
        await self.db.refresh(db_title)
        
        return db_title
    

    async def get_existing_title(self, name: str, trailer_link: str) -> Title:
        
        if not name and not trailer_link:
            raise exceptions.NoTitleData
        
        title = await TitleDAO.find_one_or_none(self.db, or_(
            Title.name == name,
            Title.trailer_link == trailer_link,
            ))
        
        return title
    
    
    async def get_all_titles(self, offset: int = 0, limit: int = 10, **filter_by) -> List[Title]:
        
        titles = await TitleDAO.find_all(self.db, *filter, offset=offset, limit=limit, **filter_by)
        
        return titles


class EpisodeCrud:
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_episode(self, anime_id: int, episode: schemas.EpisodeCreate):
        
        episode_exist = await self.get_existing_episode(trailer_link=episode.episode_link)
        
        if episode_exist:
            raise exceptions.EpisodeAlreadyExists
        
        db_episode = await EpisodeDAO.add(
            self.db,
            schemas.EpisodeCreate(
            **episode.model_dump(),
            anime_id = anime_id,
            )
        )

        self.db.add(db_episode)
        await self.db.commit()
        await self.db.refresh(db_episode)
        
        return db_episode
        
    
    async def get_existing_episode(self, episode_link: str) -> Episode:
        
        if not episode_link:
            raise exceptions.NoEpisodeData
        
        episode = EpisodeDAO.find_one_or_none(self.db, Episode.episode_link == episode_link)
        
        return episode


    async def get_all_episodes(self, anime_id: int, offset: int = 0, limit: int = 10, **filter_by):
        
        episodes = await EpisodeDAO.find_all(self.db, *filter, offset=offset, limit=limit, **filter_by)
        
        return episodes
    