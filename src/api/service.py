from typing import List
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_
from sqlalchemy.future import select

from .models import Title, Episode
from .dao import TitleDAO, EpisodeDAO
from . import schemas, exceptions


class TitleCRUD:
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_title(self, title: schemas.TitleCreate) -> Title:
        
        title_exist = await self.get_existing_title(name=title.name, trailer_link=title.trailer_link)
        
        if title_exist:
            raise exceptions.TitleAlreadyExists
        
        id = str(uuid4())
        
        db_title = await TitleDAO.add(
            self.db,
            schemas.TitleCreateDB(
            **title.model_dump(),
            id = id,
            )
        )

        self.db.add(db_title)
        await self.db.commit()
        await self.db.refresh(db_title)
        
        return db_title
    

    async def get_existing_title(self, title_id: str = None, name: str = None, trailer_link: str = None) -> Title:
        
        if not name and not trailer_link and not title_id:
            
            raise exceptions.NoTitleData
        
        title = await TitleDAO.find_one_or_none(self.db, or_(
            Title.id == title_id,
            Title.name == name,
            Title.trailer_link == trailer_link,
            ))
        
        return title
    
    
    async def get_all_titles(self, offset: int = 0, limit: int = 10, *filter, **filter_by) -> List[Title]:
        
        titles = await TitleDAO.find_all(self.db, *filter, offset=offset, limit=limit, **filter_by)
        
        return titles
    
    
    async def delete_title(self, title_id: str = None, title_name: str = None):
        
        if not title_id and not title_name:
            raise exceptions.NoTitleData
        
        title = await self.get_existing_title(title_id=title_id, name=title_name)
        
        if not title:
            raise exceptions.TitleWasNotFound
        
        await TitleDAO.delete(self.db, or_(
            title_id == Title.id,
            title_name == Title.name))
        
        await self.db.commit()
        
        return {"Message": "Deleting successful"}


class EpisodeCRUD:
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_episode(self, episode: schemas.EpisodeCreate):
        
        episode_exist = await self.get_existing_episode(episode_link=episode.episode_link)
        
        if episode_exist:
            raise exceptions.EpisodeAlreadyExists
        
        db_episode = await EpisodeDAO.add(
            self.db,
            schemas.EpisodeCreate(
            **episode.model_dump(),
            )
        )

        self.db.add(db_episode)
        await self.db.commit()
        await self.db.refresh(db_episode)
        
        return db_episode
        
    
    async def get_existing_episode(self,
        title_id: str = None,
        episode_link: str = None,
        episode_number: str = None,
        ) -> Episode:
        
        if not episode_link and not (episode_number and title_id):
            raise exceptions.NoEpisodeData
        
        episode = await EpisodeDAO.find_one_or_none(
        self.db,
        or_(Episode.episode_link == episode_link,
        and_(Episode.episode_number == episode_number,
             Episode.title_id == title_id))
        )
        

        return episode


    async def get_all_episodes(self, offset: int, limit: int, title_id: str):

        episodes = await EpisodeDAO.find_all(self.db, offset=offset, limit=limit, title_id=title_id)
        
        return episodes
    
    
    async def delete_episode(self,
        title_id: str = None,
        title_name: str = None,
        episode_number: int = None,
        episode_title: str = None,
        ):
        
        if not title_id and not title_name:
            raise exceptions.NoTitleData
        
        if not episode_number and not episode_title:
            raise exceptions.NoEpisodeData
        
        
        title = await TitleCRUD.get_existing_title(self, title_id=title_id, name=title_name)
        
        if not title:
            raise exceptions.TitleWasNotFound
        
        episode = await self.get_existing_episode(title_id=title_id, episode_number=episode_number)
        
        if not episode:
            raise exceptions.EpisodeDoesNotExist
        
        await EpisodeDAO.delete(self.db, 
        or_(title_id == Title.id, title_name == Title.name),
        and_(or_(episode_number == Episode.episode_number, episode_title == Episode.episode_title )))
        
        await self.db.commit()
        
        return {"Message": "Deleting successful"}
    

class DatabaseManager:
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.title_crud = TitleCRUD(db)
        self.episode_crud = EpisodeCRUD(db)

    # Применение изменений к базе данных
    async def commit(self):
        await self.db.commit()
    