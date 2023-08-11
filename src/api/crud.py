from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from sqlalchemy.future import select

from .models import Anime, Episode
from . import schemas, exceptions


async def create_anime(db: AsyncSession, anime: schemas.AnimeBase):
    db_anime = Anime(
        title=anime.title,
        trailer_link=anime.trailer_link,
        num_episodes=anime.num_episodes,
        synopsis=anime.synopsis,
        japanese_title = anime.japanese_title, 
        country = anime.country, 
        year = anime.year, 
        genres = anime.genres, 
        rating = anime.rating, 
        type = anime.type, 
        status = anime.status, 
        studio = anime.studio, 
        MPAA = anime.MPAA,  
        duration = anime.duration,
        small_img = anime.small_img,
        big_img = anime.big_img,
        screens = anime.screens,
    )
    db.add(db_anime)
    await db.commit()
    await db.refresh(db_anime)
    
    return db_anime


async def create_episode(db: AsyncSession, anime_id: int, episode: schemas.EpisodeCreate):
    
    last_episode_number = await get_last_episode(db, anime_id) + 1
        
        
    db_episode = Episode(
        episode_number=last_episode_number,
        episode_title=episode.episode_title,
        episode_link=episode.episode_link,
        anime_id=episode.anime_id,
        translations = episode.translations,
    )
    db.add(db_episode)
    await db.commit()
    await db.refresh(db_episode)
    
    return db_episode


async def get_existing_anime(db: AsyncSession, title: str):
    query = select(Anime).where(Anime.title == title)
    
    result = await db.execute(query)
    anime = result.scalar_one_or_none()
    
    return anime


async def get_last_episode(db: AsyncSession, anime_id: int):
    
    query = (
        select(Episode.episode_number)
        .where(Episode.anime_id == anime_id)
        .order_by(Episode.episode_number.desc())
        .limit(1)
    )
    
    result = await db.execute(query)
    last_episode = result.scalars().first()
    
    return last_episode or 0


async def get_existing_episode_link(db: AsyncSession, episode_link: str):
    query = select(Episode).where(Episode.episode_link == episode_link)
    
    result = await db.execute(query)
    episode_link = result.scalar_one_or_none()
    
    return episode_link
    
    
async def read_anime_by_id_or_title(db: AsyncSession, anime_id: int = None, title: str = None):
    if not anime_id and not title:
        raise ValueError("Either 'anime_id' or 'title' must be provided.")

    stmt = select(Anime).where(
        or_(Anime.id == anime_id, Anime.title == title)
    )

    result = await db.execute(stmt)
    anime = result.scalar_one_or_none()

    if anime is None:
        raise exceptions.InvalidCredentials

    return anime


async def read_all_animes(db: AsyncSession, skip: int = 0, limit: int = 10):
    stmt = select(Anime).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    
    return result.scalars().all()


async def read_all_episodes_for_anime(db: AsyncSession, anime_id: int, skip: int = 0, limit: int = 10):
    stmt = select(Episode).where(Episode.anime_id == anime_id).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    
    return result.scalars().all()


    