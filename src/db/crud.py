from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from sqlalchemy.future import select

from .models import Anime, Episode
from . import schemas


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


async def create_episode(db: AsyncSession, anime_id: int, episode: schemas.EpisodeBase):
    db_episode = Episode(
        episode_title=episode.episode_title,
        episode_link=episode.episode_link,
        anime_id=anime_id,
        translations = episode.translations,
    )
    db.add(db_episode)
    await db.commit()
    await db.refresh(db_episode)
    return db_episode


async def check_existing_anime(db: AsyncSession, title: str):
    stmt = select(Anime).where(Anime.title == title)
    result = await db.execute(stmt)
    anime = result.scalar_one_or_none()
    return anime
    
    
    
async def read_anime_by_id_or_title(db: AsyncSession, anime_id: int = None, title: str = None):
    if not anime_id and not title:
        raise ValueError("Either 'anime_id' or 'title' must be provided.")

    stmt = select(Anime).where(
        or_(Anime.id == anime_id, Anime.title == title)
    )

    result = await db.execute(stmt)
    anime = result.scalar_one_or_none()

    if anime is None:
        raise HTTPException(
            status_code=404,
            detail="Unknown ID or title"
            )

    return anime


async def read_all_animes(db: AsyncSession, skip: int = 0, limit: int = 10):
    stmt = select(Anime).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def read_all_episodes_for_anime(db: AsyncSession, anime_id: int, skip: int = 0, limit: int = 10):
    stmt = select(Episode).where(Episode.anime_id == anime_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


    